#!/usr/bin/env bash
# Python Virtual Environment Setup Script
# =========================================
# Automatically discovers installed Python versions and creates/validates
# virtual environments for each version.
#
# Usage:
#   ./setup_venv.sh
#
# Features:
#   - Auto-discovers Python installations in /usr/bin and /usr/local/bin
#   - Creates virtual environments named venv_<version> (e.g., venv_3.14)
#   - Validates existing venvs and recreates if corrupted or mismatched
#   - Installs/upgrades pip in each venv
#   - Installs requirements.txt if present
#   - Runs in subshell to avoid polluting parent environment
#
# Virtual Environment Validation:
#   - Checks if venv directory exists
#   - Verifies activate script is present
#   - Confirms Python version matches expected version
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2024-2026. Licensed under the MIT License.

declare -A python_version_to_path=()

# Discovers installed Python versions and maps version -> path
# Searches /usr/bin and /usr/local/bin for non-symlink Python executables
# Populates python_version_to_path associative array
find_installed_python_versions() {
    local -a python_paths
    local version
    python_paths=(/usr/bin/python* /usr/local/bin/python*)
    for python_path in "${python_paths[@]}"; do
        if [[ -x "${python_path}" && ! -L "${python_path}" ]]; then
            version=$("${python_path}" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
            if [[ -n "${version}" ]]; then
                python_version_to_path["${version}"]="${python_path}"
            fi
        fi
    done
}

# Creates or validates virtual environment for specified Python version
# Args:
#   $1 - Python version (e.g., "3.14")
# Returns:
#   0 - Success (venv created or validated)
#   1 - Python version not found
# Creates venv_<version> directory and installs/upgrades pip
setup_venv(){
    local pycmd="${python_version_to_path[$1]}"
    local venv_dir="venv_$1"
    local reported_version
    local needs_install=false

    if [[ ! -v python_version_to_path["$1"] ]]; then
        printf "[ERROR] Python %s not found in installed versions\n" "$1"
        return 1
    fi

    if [[ ! -d "${venv_dir}" ]]; then
        printf "[INFO] Virtual environment directory %s does not exist\n" "${venv_dir}"
        needs_install=true
    elif [[ ! -f "${venv_dir}/bin/activate" ]]; then
        printf "[WARN] Activate script not found in %s\n" "${venv_dir}"
        needs_install=true
    else
        reported_version=$(
            bash -c "
                source '${venv_dir}/bin/activate'
                python --version 2>&1 | grep -oP '\d+\.\d+' | head -1
            "
        )
        if [[ "${reported_version}" == "$1" ]]; then
            printf "[INFO] Virtual environment for Python %s is valid\n" "$1"
        else
            printf "[WARN] Version mismatch in virtual environment %s\n" "${venv_dir}"
            needs_install=true
        fi
    fi

    if [[ "${needs_install}" == true ]]; then
        rm -rf "${venv_dir}"
        printf "[INFO] Creating virtual environment for Python %s in %s\n" "$1" "${venv_dir}"
        "${pycmd}" -m venv "${venv_dir}"
        printf "[INFO] Virtual environment created successfully\n"
    fi
    local max_width=80
    (
        source "${venv_dir}/bin/activate"
        python --version
        python -m pip --version || python -m ensurepip
        python -m pip install pip --upgrade
        [[ -f requirements.txt ]] && python -m pip install -r requirements.txt --upgrade
    ) | while read -r line; do
        if [[ ${#line} -gt ${max_width} ]]; then
            local half=$((max_width / 2 - 2))
            line="${line:0:${half}}...${line: -${half}}"
        fi
        printf "\t %s\n" "${line}"
    done
}

# ============================================================================
# Script Execution Guard
# ============================================================================
# Only run if script is executed directly (not sourced)
# This allows the script to be imported as a library without side effects
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    find_installed_python_versions
    for version in "${!python_version_to_path[@]}"; do
        setup_venv "${version}"
    done
fi
