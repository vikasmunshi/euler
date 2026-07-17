#!/usr/bin/env bash
#
# Whole-tree audit of what git actually stores. Two independent checks:
#   audit_private  — every tracked file under solutions/private is ciphertext.
#   audit_binaries — no tracked file anywhere is a compiled binary.
#
# This is the periodic full sweep. The git hooks carry their own inlined copies of
# both checks, scoped to the blobs at hand (pre-commit: staged; pre-push: what the
# push would add), so they stay fast and never re-examine settled history. This
# script is what covers that history.
set -e  # Exit on error

declare summary=0
declare private_dir="solutions/private"
# The interpreter for the checks below: it must be the venv's, since audit_private imports
# solver.crypto. Bare `python` is correct from an activated venv (the dev shell), which is
# the default; callers that only know the venv by path — the Makefile, and the `git-audit`
# command when the web shell's PATH has no venv on it — pass PYTHON explicitly.
declare python="${PYTHON:-python}"

audit_private() {
    # audit_private — Verify every tracked file under solutions/private is encrypted at rest.
    #
    # Reads each path's stored git blob directly via 'git cat-file' (the object store, so NO smudge
    # filter runs) and checks it begins with the gitfilter MAGIC header. The magic is read from
    # solver.crypto.ciphers.config_dict so this stays in lockstep with the filter. A blob that
    # does not start with the magic is plaintext — a file that slipped past the clean filter (e.g.
    # committed before .gitattributes covered it, or with the filter uninstalled).
    #
    #   With summary=1: prints only the counts, not the per-file list.
    #
    # Returns 1 if any tracked private file is stored as plaintext, else 0.
    local magic_hex mlen total=0 encrypted=0 plaintext=0
    magic_hex=$("${python}" -c 'from solver.crypto.config import config; print(config["magic"].hex())')
    mlen=$(( ${#magic_hex} / 2 ))

    echo "Encryption-at-rest audit of tracked ${private_dir} (magic=0x${magic_hex}):"

    local entry meta path sha head_hex
    while IFS= read -r -d '' entry; do
        # 'git ls-files -s' entry format: "<mode> <sha> <stage>\t<path>"
        meta=${entry%%$'\t'*}
        path=${entry#*$'\t'}
        sha=$(awk '{print $2}' <<<"${meta}")
        head_hex=$(git cat-file -p "${sha}" | head -c "${mlen}" | xxd -p)
        total=$(( total + 1 ))
        if [[ "${head_hex}" == "${magic_hex}" ]]; then
            encrypted=$(( encrypted + 1 ))
            [[ "${summary}" -eq 0 ]] && printf "  ENCRYPTED    %s\n" "${path}"
        else
            plaintext=$(( plaintext + 1 ))
            printf "  !! PLAINTEXT %s\n" "${path}"
        fi
    done < <(git ls-files -sz -- "${private_dir}")

    if [[ "${total}" -eq 0 ]]; then
        echo "  (no tracked files under ${private_dir})"
        return 0
    fi

    printf "Summary: %d encrypted, %d plaintext, %d total\n" "${encrypted}" "${plaintext}" "${total}"
    [[ "${plaintext}" -eq 0 ]]
}

audit_binaries() {
    # audit_binaries — Verify no tracked file anywhere in the tree is a compiled binary.
    #
    # The C runner compiles each solution to an executable (p<NNNN>_s<K>_c, no extension);
    # those are gitignored build artifacts, regenerated on demand, that must never enter git.
    # Reads every tracked blob from the object store and flags any beginning with the ELF
    # magic (7f 45 4c 46). Unlike audit_private this drives a single 'git cat-file --batch'
    # process rather than one cat-file per file: the scope is the whole tree (~5k files), and
    # per-file processes would take minutes.
    #
    #   With summary=1: prints only the counts, not the per-file list.
    #
    # Returns 1 if any tracked file is stored as a compiled binary, else 0.
    echo "Compiled-binary audit of the tracked tree (magic=0x7f454c46):"
    "${python}" - "${summary}" <<'PY'
import subprocess
import sys

summary = sys.argv[1] == "1"
ELF = b"\x7fELF"

out = subprocess.run(["git", "ls-files", "-sz"], capture_output=True, check=True).stdout
items = []
for entry in out.split(b"\0"):
    if not entry:
        continue
    # 'git ls-files -sz' entry format: "<mode> <sha> <stage>\t<path>"
    meta, path = entry.split(b"\t", 1)
    fields = meta.split()
    if fields[0] == b"160000":          # gitlink: a submodule commit, not a blob
        continue
    items.append((fields[1].decode(), path.decode()))

proc = subprocess.Popen(["git", "cat-file", "--batch"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
assert proc.stdin and proc.stdout
total = binaries = 0
for sha, path in items:
    proc.stdin.write((sha + "\n").encode())
    proc.stdin.flush()
    header = proc.stdout.readline().split()
    if len(header) < 3 or header[1] != b"blob":
        continue                       # missing object: nothing to read
    size = int(header[2])
    content = proc.stdout.read(size)
    proc.stdout.read(1)                # trailing newline after the content
    total += 1
    if content[:4] == ELF:
        binaries += 1
        print(f"  !! BINARY    {path}")
    elif not summary:
        print(f"  OK           {path}")
proc.stdin.close()
proc.wait()

if total == 0:
    print("  (no tracked files)")
    sys.exit(0)
print(f"Summary: {total - binaries} ok, {binaries} binary, {total} total")
sys.exit(1 if binaries else 0)
PY
}

main() {
    cd "$(git rev-parse --show-toplevel)"
    local rc=0
    audit_private || rc=1
    echo
    audit_binaries || rc=1
    return "${rc}"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" --summary "* ]] && summary=1
    main
fi