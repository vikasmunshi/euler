#!/usr/bin/env bash
dir_to_check=$1
if [[ -z "${dir_to_check}" ]]; then
    echo "Error: Directory to check must be provided as first argument" >&2
    exit 1
fi

# trailing-whitespace: auto-fix all text files in ${dir_to_check}, mirroring
# the pre-commit hook (scripts/setup/hooks/pre-commit.template). Globs match
# the same families flagged by `git diff --check`. Add new extensions here
# when the repo grows to include them.
fix_files=$(find "${dir_to_check}" -type f \( \
    -name '*.py' -o -name '*.c' -o -name '*.h' -o -name '*.html' \
    -o -name '*.json' -o -name '*.md' -o -name '*.sh' -o -name '*.txt' \
    -o -name '*.template' -o -name '*.yml' -o -name '*.yaml' \))
if [[ -n "$fix_files" ]]; then
    echo "$fix_files" | xargs -d '\n' sed -i 's/[[:space:]]*$//'
fi

# trailing-whitespace: check remaining changes (exclude encrypted files)
echo "checking trailing-whitespace ${dir_to_check} ..."
git diff --check --no-color -- "${dir_to_check}" ':!*.enc'
ws_rc=$?
echo "trailing-whitespace ${dir_to_check} -> ${ws_rc}"

# Check if there are Python files
if ! find "${dir_to_check}" -type f -name "*.py" | grep -q .; then
    echo "No Python files found in ${dir_to_check}, skipping mypy"
    mypy_rc=0
else
    echo "checking mypy ${dir_to_check} ..."
    mypy "${dir_to_check}"
    mypy_rc=$?
    echo "mypy ${dir_to_check} -> ${mypy_rc}"
fi

echo "checking flake8 ${dir_to_check} ..."
flake8 "${dir_to_check}"
flake8_rc=$?
echo "flake8 ${dir_to_check} -> ${flake8_rc}"

# Shell lint — the shell half of the tree, held to the same bar as the Python half.
# (This comment does not open with the tool's name: a comment starting `# shellcheck`
# in front of a command is read as a *directive*, and an unparseable one is an error.)
# The git-hook templates are shell too — they only become .git/hooks/* once
# githooks.sh substitutes __VENV__ — so they are linted alongside the scripts that
# render them. Options come from .shellcheckrc at the repo root — shared with the git
# hooks and your editor — so nothing is configured on this command line. shellcheck is
# a base apt package (scripts/setup/dev_env.sh), so a missing binary is a broken
# install, not an opt-out — it fails.
# The file list goes through an array rather than `| xargs`, so the reported code is
# the linter's own 1 and not xargs' 123 — the lanes' codes are summed for the exit
# status below, where a needlessly large one is both misleading and closer to the
# wrap at 256.
mapfile -t sh_files < <(find "${dir_to_check}" -type f \( -name '*.sh' -o -name '*.template' \))
if (( ${#sh_files[@]} == 0 )); then
    echo "No shell scripts found in ${dir_to_check}, skipping shellcheck"
    shellcheck_rc=0
elif ! command -v shellcheck > /dev/null 2>&1; then
    echo "Error: shellcheck is not installed — run 'make install-system'" >&2
    shellcheck_rc=1
else
    echo "checking shellcheck ${dir_to_check} ..."
    shellcheck -- "${sh_files[@]}"
    shellcheck_rc=$?
    echo "shellcheck ${dir_to_check} -> ${shellcheck_rc}"
fi

# the interaction guard: `dialogue.interactive` must be called through its module, never
# bound by import. A by-value copy is a second seam that `--silent` and the tests cannot
# reach, so a command would prompt when it must not (docs/developer-guide.md §3.10).
seam_rc=0
if grep -rn 'from solver.shell.dialogue import.*\binteractive\b' "${dir_to_check}" --include='*.py'; then
    echo "^ import the module and call dialogue.interactive() instead" >&2
    seam_rc=1
fi
echo "interaction guard ${dir_to_check} -> ${seam_rc}"

# command docstrings: the standard in docs/developer-guide.md §3.8, enforced by the
# `check-commands` shell command. Only meaningful for the solver package — the command
# registry is what it walks, and only an admin subject sees all of it (the command is
# admin-floored, so a lesser profile finds no such command and this step is skipped).
doclint_rc=0
if [[ "${dir_to_check}" == solver || "${dir_to_check}" == */solver ]]; then
    echo "checking command docstrings ..."
    solver "check-commands"
    doclint_rc=$?
    echo "command docstrings -> ${doclint_rc}"
fi

exit $(( "${ws_rc}" + "${mypy_rc}" + "${flake8_rc}" + "${shellcheck_rc}" + "${seam_rc}" + "${doclint_rc}" ))