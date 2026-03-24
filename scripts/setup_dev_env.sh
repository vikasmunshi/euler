#!/usr/bin/env bash
# Development Environment Installation Script
# ============================================
# Manages C/C++, Lua, Python, and Ruby development environments on Ubuntu/Debian.
#
# Usage:
#   ./setup_dev_env.sh [--dry-run] {install|uninstall|status} {all|c|lua|python|ruby} [...]
#
# Commands:
#   install   - Install development environment(s) (default: all)
#   uninstall - Uninstall development environment(s) (default: all, protects base packages)
#   status    - Show installation status (default command and target)
#
# Targets:
#   all    - All environments (C/C++, Lua, Python, Ruby)
#   c      - C/C++ (GCC, clang, cmake, gdb, valgrind, autotools)
#   lua    - Lua 5.4 (runtime and dev packages)
#   python - Python 3.12, 3.13, 3.14, 3.15 (system default protected)
#   ruby   - Ruby (runtime, dev, gems)
#
# Examples:
#   ./setup_dev_env.sh                    # Show status (all)
#   ./setup_dev_env.sh install c lua      # Install C/C++ and Lua
#   ./setup_dev_env.sh uninstall python   # Uninstall Python (protects system default)
#   ./setup_dev_env.sh --dry-run install all  # Test without changes
#
# Features:
#   - Dry-run mode for safe testing
#   - Auto-detects and protects system Python version
#   - Deactivates venvs before install/uninstall
#   - Installs pip via ensurepip for non-system Python versions
#   - Never removes base packages or PPAs
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2024-2026. Licensed under the MIT License.

# ============================================================================
# Package Array Definitions
# ============================================================================
# Base packages (git, build-essential, software-properties-common) - never removed
declare -a base_packages=("git" "gh" "build-essential" "software-properties-common")
# shellcheck disable=SC2034 # used dynamically
declare -a base_commands=("git" "gh" "make")

# PPAs (deadsnakes/ppa for Python) - never removed
# PPAs (deadsnakes/ppa for Python) - never removed
# Notes:
#   base_packages: git, build-essential, software-properties-common
#   package_ppas: ppa:deadsnakes/ppa
declare -a package_ppas=("ppa:deadsnakes/ppa")

# Valid targets: dynamically populated as c, lua, ruby, python
declare -a all_targets=()

# ============================================================================
# C/C++ (build-essential in base_packages provides gcc, g++, make, libc-dev)
# ============================================================================
all_targets+=(c)
# shellcheck disable=SC2034 # used dynamically
declare -a c_packages=(
    "autoconf" "automake" "clang" "clang-format" "clang-tidy" "cmake" "gdb"
    "libc++-dev" "libc++abi-dev" "libtool" "lldb" "pkg-config" "valgrind"
)
# shellcheck disable=SC2034 # used dynamically
declare -a c_commands=(
    "autoconf" "automake" "clang" "clang++" "clang-format" "clang-tidy" "cmake"
    "g++" "gcc" "gdb" "libtool" "lldb" "pkg-config" "valgrind"
)
# shellcheck disable=SC2034 # used dynamically
declare -a c_versions=("C" "C++")

# ============================================================================
# Lua
# ============================================================================
all_targets+=(lua)
# shellcheck disable=SC2034 # used dynamically
declare -a lua_packages=("lua5.4" "liblua5.4-dev")
# shellcheck disable=SC2034 # used dynamically
declare -a lua_commands=("lua" "luac")

# ============================================================================
# Ruby
# ============================================================================
all_targets+=(ruby)
# shellcheck disable=SC2034 # used dynamically
declare -a ruby_packages=("ruby" "ruby-dev" "ruby-git")
# shellcheck disable=SC2034 # used dynamically
declare -a ruby_commands=("ruby" "gem" "irb" "rake" "ri")

# ============================================================================
# Python (system default auto-detected and protected)
# ============================================================================
all_targets+=(python)
declare -a python_versions=("3.12" "3.13" "3.14" "3.15")
declare -a python_packages=()
for version in "${python_versions[@]}"; do
    python_packages+=("python${version}" "python${version}-dev" "python${version}-venv")
done
declare -a python_commands=("python3")
for version in "${python_versions[@]}"; do
    python_commands+=("python${version}")
done

# ============================================================================
# Package Management Arrays
# ============================================================================
declare -a packages=()           # Combined packages to install/uninstall
declare -a commands=()           # Combined commands to check
declare -a installed_packages=() # Currently installed packages

# ============================================================================
# Helper Functions
# ============================================================================

# Function: populate_packages
# Description: Populates packages/commands arrays from targets (sorted, deduplicated)
populate_packages() {
    packages=()
    commands=()
    for target in "$@"; do
        local -n packages_ref="${target}_packages"
        local -n commands_ref="${target}_commands"
        packages+=("${packages_ref[@]}")
        commands+=("${commands_ref[@]}")
    done
    if [[ ${#packages[@]} -gt 0 ]]; then
        mapfile -t packages < <(printf '%s\n' "${packages[@]}" | sort -u)
    fi
    if [[ ${#tools[@]} -gt 0 ]]; then
        mapfile -t tools < <(printf '%s\n' "${tools[@]}" | sort -u)
    fi
}

# Function: populate_installed
# Description: Filters packages array to only installed packages (via dpkg)
populate_installed() {
    installed_packages=()
    for pkg in "${packages[@]}"; do
        if dpkg -l "$pkg" 2>/dev/null | grep -q "^ii\s\+${pkg}"; then
            installed_packages+=("$pkg")
        fi
    done
    if [[ ${#installed_packages[@]} -gt 0 ]]; then
        mapfile -t installed_packages < <(printf '%s\n' "${installed_packages[@]}" | sort -u)
    fi
}

# System default python version
declare python_system_version

# Function: find_python_system_version
# Description: Deactivates venv (if active), detects system Python version, sets python_system_version global
find_python_system_version() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        printf "→ Deactivating Python virtual environment: %s\n" "$VIRTUAL_ENV"
        local venv_path="$VIRTUAL_ENV"
        if declare -f deactivate >/dev/null 2>&1; then
            deactivate 2>/dev/null || true
        fi
        unset VIRTUAL_ENV
        unset VIRTUAL_ENV_PROMPT
        if [[ -n "$venv_path" ]]; then
            PATH="${PATH//${venv_path}\/bin:/}"
            PATH="${PATH%:}"
            export PATH
        fi
        unset PYTHONHOME
    fi
    python_system_version="$(python3 --version 2>&1 | grep -oP 'Python \K3\.\d+' )"
}

# Function: ensure_essentials
# Description: Add PPAs and repos and install packages if missing (idempotent)
ensure_essentials() {
    execute_with_dry_run sudo apt update >/dev/null 2>&1
    for ppa in "${package_ppas[@]}"; do
        local ppa_name="${ppa#ppa:}"
        local ppa_user="${ppa_name%%/*}"
        local ppa_repo="${ppa_name#*/}"
        if ! grep -rq "${ppa_user}.*${ppa_repo}" /etc/apt/sources.list.d/ 2>/dev/null && \
           ! grep -q "${ppa_user}.*${ppa_repo}" /etc/apt/sources.list 2>/dev/null; then
            execute_with_dry_run sudo add-apt-repository -y "$ppa"
            execute_with_dry_run sudo apt update >/dev/null 2>&1
        fi
    done
    if ! grep -q "cli.github.com/packages" /etc/apt/sources.list.d/github-cli.list 2>/dev/null; then
        execute_with_dry_run sudo mkdir -p -m 755 /etc/apt/keyrings
        local gh_keyring="/etc/apt/keyrings/githubcli-archive-keyring.gpg"
        if [[ ! -f "$gh_keyring" ]]; then
            local tmp_key
            tmp_key=$(mktemp)
            execute_with_dry_run wget -nv -O"$tmp_key" https://cli.github.com/packages/githubcli-archive-keyring.gpg
            execute_with_dry_run sudo tee "$gh_keyring" < "$tmp_key" >/dev/null
            execute_with_dry_run rm -f "$tmp_key"
            execute_with_dry_run sudo chmod go+r "$gh_keyring"
        fi
        execute_with_dry_run sudo mkdir -p -m 755 /etc/apt/sources.list.d
        printf "deb [arch=%s signed-by=%s] https://cli.github.com/packages stable main\n" \
            "$(dpkg --print-architecture)" "$gh_keyring" | \
            execute_with_dry_run sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
        execute_with_dry_run sudo apt update >/dev/null 2>&1
    fi
    local -a packages_to_install=()
    for pkg in "${base_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii\s\+${pkg}\s"; then
            packages_to_install+=("$pkg")
        fi
    done
    if [[ ${#packages_to_install[@]} -gt 0 ]]; then
        execute_with_dry_run sudo apt install -y "${packages_to_install[@]}"
    fi
}

# Function: python_ensurepip ($1=version)
# Description: Installs pip via ensurepip if not already available (idempotent)
python_ensurepip() {
    local version="$1"
    if "python${version}" -m pip --version >/dev/null 2>&1; then
        return 0
    fi
    execute_with_dry_run "python${version}" -m ensurepip
}

# Function: python_uninstall_user_site_packages ($1=version)
# Description: Removes user site-packages and pip for non-system Python versions
python_uninstall_user_site_packages() {
    local version="$1"
    if ! command -v "python${version}" >/dev/null 2>&1; then
        return 0
    fi
    local user_site_packages
    user_site_packages=$("python${version}" -m site --user-site 2>/dev/null || echo "")
    if [[ -n "$user_site_packages" ]] && [[ -d "$user_site_packages" ]]; then
        execute_with_dry_run rm -rf "$user_site_packages"
    fi
    local user_pip="${HOME}/.local/bin/pip${version}"
    if [[ -f "$user_pip" ]]; then
        execute_with_dry_run rm -f "$user_pip"
    fi
}
# ============================================================================
# Main Action Functions
# ============================================================================

# Function: install ($@=targets)
# Description: Installs packages for targets (ensures base packages/PPAs, runs ensurepip for non-system Python)
install() {
    ensure_essentials
    populate_packages "$@"
    populate_installed
    local -a packages_to_install=()
    for pkg in "${packages[@]}"; do
        if ! printf '%s\n' "${installed_packages[@]}" | grep -q "^${pkg}$"; then
            packages_to_install+=("$pkg")
        fi
    done
    if [[ ${#packages_to_install[@]} -eq 0 ]]; then
        printf "→ No packages to install\n"
        return 0
    fi
    printf "→ Installing packages: %s\n" "${packages_to_install[*]}"
    execute_with_dry_run sudo apt install -y "${packages_to_install[@]}"
    if printf '%s\n' "$@" | grep -q "^python$"; then
        find_python_system_version
        for version in "${python_versions[@]}"; do
            if [[ "$version" != "$python_system_version" ]]; then
                python_ensurepip "$version"
            fi
        done
    fi
    printf "\n→ Installation complete!\n"
}

# Function: uninstall ($@=targets)
# Description: Uninstalls packages (protects base packages, system Python, cleans user site-packages)
uninstall() {
    local -a filtered_targets=()
    for target in "$@"; do
        if [[ "$target" != "base" ]]; then
            filtered_targets+=("$target")
        fi
    done
    populate_packages "${filtered_targets[@]}"
    populate_installed
    if printf '%s\n' "$@" | grep -q "^python$"; then
        find_python_system_version
        local -a filtered_packages=()
        for pkg in "${installed_packages[@]}"; do
            if [[ "$pkg" != "python${python_system_version}" ]]; then
                filtered_packages+=("$pkg")
            fi
        done
        installed_packages=("${filtered_packages[@]}")
        for version in "${python_versions[@]}"; do
            if [[ "$version" != "$python_system_version" ]]; then
                python_uninstall_user_site_packages "$version"
            fi
        done
    fi
    if [[ ${#installed_packages[@]} -eq 0 ]]; then
        printf "→ No packages to uninstall\n"
        return 0
    fi
    printf "→ Uninstalling packages: %s\n" "${installed_packages[*]}"
    execute_with_dry_run sudo apt purge -y "${installed_packages[@]}"
    execute_with_dry_run sudo apt autoremove -y
    printf "\n→ Uninstallation complete!\n"
}

# Function: status ($@=targets)
# Description: Shows packages (dpkg versions) and commands (runtime versions) for targets
status() {
    populate_packages "$@"
    populate_installed
    printf "Development Environment Status:\n"
    printf "================================\n"
    printf "\nPackages (apt-managed):\n"
    printf "=======================\n"
    for pkg in "${packages[@]}"; do
        if printf '%s\n' "${installed_packages[@]}" | grep -q "^${pkg}$"; then
            local version
            version=$(dpkg-query -W -f='${Version}' "$pkg" 2>/dev/null || echo "unknown")
            printf "  ✓ %-30s : %s\n" "$pkg" "$version"
        else
            printf "  ✗ %-30s : not installed\n" "$pkg"
        fi
    done
    printf "\nCommands (executables):\n"
    printf "=======================\n"
    for clicmd in "${commands[@]}"; do
        if command -v "$clicmd" &>/dev/null; then
            printf "  ✓ %-12s : " "$clicmd"
            ("$clicmd" --version 2>/dev/null || "$clicmd" -v 2>/dev/null) | head -n 1
        else
            printf "  ✗ %-12s : not available\n" "$clicmd"
        fi
    done
    printf "\n"
}

# ============================================================================
# Usage and Help
# ============================================================================

# Function: usage
# Description: Displays help text with commands, targets, and examples
usage() {
    printf "Usage: %s [OPTIONS] [COMMAND] [TARGETS...]\n" "$0"
    printf "       %s [COMMAND]                           (implies: all targets)\n" "$0"
    printf "       %s                                     (implies: status all)\n" "$0"
    printf "\n"
    printf "Manages development environments (C/C++, Lua, Python, Ruby) on Ubuntu/Debian.\n"
    printf "Automatically protects base packages, PPAs, and system Python version.\n"
    printf "\n"
    printf "OPTIONS:\n"
    printf "  --help      Display this help message and exit\n"
    printf "  --dry-run   Preview commands without executing (test mode)\n"
    printf "\n"
    printf "COMMANDS (default: status):\n"
    printf "  install     Install packages for specified target(s)\n"
    printf "  uninstall   Remove packages for specified target(s)\n"
    printf "  status      Show installation status for specified target(s)\n"
    printf "\n"
    printf "TARGETS (default: all):\n"
    printf "  all         All development environments\n"
    for target in "${all_targets[@]}"; do
        case "$target" in
            c)
                printf "  c           C/C++ (gcc, g++, clang, cmake, gdb, valgrind, autotools)\n"
                ;;
            lua)
                printf "  lua         Lua 5.4 (runtime, compiler, dev libraries)\n"
                ;;
            ruby)
                printf "  ruby        Ruby (runtime, gems, dev libraries)\n"
                ;;
            python)
                local -n versions_ref="${target}_versions"
                local versions_str
                versions_str=$(printf "%s, " "${versions_ref[@]}" | sed 's/, $//')
                printf "  python      Python %s (auto-detects and protects system default)\n" "$versions_str"
                ;;
            *)
                printf "  %-11s %s development environment\n" "$target" "${target^}"
                ;;
        esac
    done
    printf "\n"
    printf "PROTECTED FROM REMOVAL:\n"
    local base_packages_str
    base_packages_str=$(printf "%s, " "${base_packages[@]}" | sed 's/, $//')
    printf "  • Base packages: %s\n" "${base_packages_str}"
    local package_ppas_str
    package_ppas_str=$(printf "%s, " "${package_ppas[@]}" | sed 's/, $//')
    printf "  • Package repositories: %s\n" "${package_ppas_str}"
    printf "  • System default Python version (auto-detected)\n"
    printf "\n"
    printf "EXAMPLES:\n"
    printf "  %s                        # Show status for all environments\n" "$0"
    printf "  %s install all            # Install all environments\n" "$0"
    printf "  %s install c lua          # Install C/C++ and Lua only\n" "$0"
    printf "  %s uninstall python       # Uninstall Python (except system version)\n" "$0"
    printf "  %s status c               # Show C/C++ installation status\n" "$0"
    printf "  %s --dry-run install all  # Preview installation without changes\n" "$0"
    printf "\n"
    printf "NOTES:\n"
    printf "  • Multiple targets can be specified (e.g., 'install c lua python')\n"
    printf "  • Duplicates are automatically removed\n"
    printf "  • Options can appear anywhere in arguments\n"
    printf "  • Virtual environments are automatically deactivated before operations\n"
}

# ============================================================================
# Dry Run Support
# ============================================================================
declare dry_run=false

# Function: execute_with_dry_run ($@=command)
# Description: Logs and executes command (or skips if dry_run=true), indents output, returns exit code
execute_with_dry_run() {
    local exit_code=0
    printf "→ %s\n" "$*" >&2
    if [[ "$dry_run" == false ]]; then
        "$@" 2>&1 | sed 's/^/\t/'
        exit_code="${PIPESTATUS[0]}"
        if [[ $exit_code -eq 0 ]]; then
            printf "✓ %s [exit: %d]\n" "$*" "$exit_code" >&2
        else
            printf "✗ %s [exit: %d]\n" "$*" "$exit_code" >&2
        fi
        return "$exit_code"
    else
        printf "  [DRY RUN - skipped]\n" >&2
        return 0
    fi
}

# ============================================================================
# Main Entry Point
# ============================================================================

# Function: main ($@=arguments)
# Description: Parses args (--dry-run, action, targets), validates, expands "all", dispatches to action function
main() {
    if [[ $EUID -eq 0 ]]; then
        printf "Error: This script should not be run as root (sudo will be used when needed)\n" >&2
        exit 1
    fi
    local action=""
    local -a targets=()
    local valid_args=true
    for arg in "$@"; do
        case "$arg" in
            --help)
                usage
                return 0
                ;;
            --dry-run)
                dry_run=true
                printf "═══════════════════════════════════════════════════════════════\n" >&2
                printf "  DRY RUN MODE ENABLED - No system changes will be made\n" >&2
                printf "═══════════════════════════════════════════════════════════════\n" >&2
                ;;
            install|uninstall|status)
                if [[ ${#targets[@]} -gt 0 ]]; then
                    printf "Error: Action '%s' cannot be specified after targets: %s\n" "$arg" "${targets[*]}"
                    printf "\n"
                    valid_args=false
                fi
                if [[ -n "$action" ]]; then
                    printf "Error: Duplicate action '%s' specified (already have '%s')\n" "$arg" "$action"
                    printf "\n"
                    valid_args=false
                fi
                action="$arg"
                ;;
            all)
                [[ -z "$action" || "$action" == "status" ]] && all_targets+=(base)
                targets=("${all_targets[@]}")
                ;;
            *)
                if printf '%s\n' "${all_targets[@]}" | grep -q "^${arg}$"; then
                    targets+=("$arg")
                else
                    printf "Error: Invalid argument '%s'\n" "$arg"
                    printf "\n"
                    valid_args=false
                fi
                ;;
        esac
    done
    if [[ "$valid_args" == false ]]; then
        usage
        exit 1
    fi
    if [[ -z "$action" ]]; then
        action="status"
    fi
    if [[ ${#targets[@]} -eq 0 ]]; then
        [[ "$action" == "status" ]] && all_targets+=(base)
        targets=("${all_targets[@]}")
    fi
    mapfile -t targets < <(printf '%s\n' "${targets[@]}" | sort -u)
    printf "→ Executing: %s %s\n" "$action" "${targets[*]}"
    "$action" "${targets[@]}"
}

# ============================================================================
# Script Execution Guard
# ============================================================================
# Only run main if script is executed directly (not sourced)
# This allows the script to be imported as a library without side effects
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
