#!/usr/bin/env bash
set -e  # Exit on error

declare summary=0
declare private_dir="solutions/private"

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
    magic_hex=$(python -c 'from solver.crypto.config import config; print(config["magic"].hex())')
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

main() {
    cd "$(git rev-parse --show-toplevel)"
    audit_private
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    [[ " $* " == *" --summary "* ]] && summary=1
    main
fi