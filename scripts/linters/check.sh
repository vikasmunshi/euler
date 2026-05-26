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
    -o -name '*.yml' -o -name '*.yaml' \))
if [[ -n "$fix_files" ]]; then
    echo "$fix_files" | xargs -d '\n' sed -i 's/[[:space:]]*$//'
fi

# trailing-whitespace: check remaining changes (exclude encrypted files)
git diff --check --no-color -- "${dir_to_check}" ':!*.enc'
ws_rc=$?
echo "trailing-whitespace ${dir_to_check} -> ${ws_rc}"

# Check if there are Python files
if ! find "${dir_to_check}" -type f -name "*.py" | grep -q .; then
    echo "No Python files found in ${dir_to_check}"
    mypy_rc=0
else
    mypy "${dir_to_check}"
    mypy_rc=$?
    echo "mypy ${dir_to_check} -> ${mypy_rc}"
fi

flake8 "${dir_to_check}"
flake8_rc=$?
echo "flake8 ${dir_to_check} -> ${flake8_rc}"

exit $(( "${ws_rc}" + "${mypy_rc}" + "${flake8_rc}" ))