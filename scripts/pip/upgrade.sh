#!/usr/bin/env bash
set -e  # Exit on error

upgrade() {
    cd "$(git rev-parse --show-toplevel)"
    [[ -z "${VIRTUAL_ENV}" ]] && {
        echo "Error: Not in a Python virtual environment. Please activate your venv first."
        exit 1
    }
    python3 -c "import sys; raise SystemExit(0 if sys.prefix != sys.base_prefix else 1)" || {
        echo "Error: Not in a Python virtual environment. Please activate your venv first."
        exit 1
    }
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade "$@"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    upgrade "$@"
fi
