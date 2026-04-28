#!/usr/bin/env bash
# Chrome Setup Script
# ==================
#
# This script automates the installation or removal of Google Chrome browser on
# Debian-based Linux systems (Ubuntu, Debian, etc.). It checks if Chrome
# is already installed and if not, downloads and installs the latest
# stable version.
#
# Features:
# - Checks for existing Chrome installation
# - Installs latest stable Chrome package
# - Creates browser control script at /usr/local/bin/browser for Chrome management
# - Uninstalls Chrome cleanly
# - Handles package dependencies
# - Cleans up temporary files
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2024. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

CHROME_PKG="google-chrome-stable"
DEB_URL="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
BROWSER_SCRIPT="/usr/local/bin/browser"

usage() {
    echo "Usage: $0 [install|uninstall]"
    echo
    echo "  install   Install Google Chrome (default if no argument given)"
    echo "  uninstall Remove Google Chrome and its configuration"
}

# Verifies that sudo is available and the current user has sudo privileges
# Prints an error and returns 1 if sudo is missing or the user is not authorised
check_can_sudo() {
    if ! command -v sudo &> /dev/null; then
        echo "Error: sudo is not installed or not found in PATH" >&2
        return 1
    fi
    if ! sudo -v 2>/dev/null; then
        echo "Error: current user does not have sudo privileges" >&2
        return 1
    fi
}

# Returns 0 if Google Chrome is installed and fully configured, 1 otherwise
chrome_is_installed() {
    dpkg-query -W -f='${Status}' "${CHROME_PKG}" 2>/dev/null | grep -q "install ok installed" \
        && command -v "${CHROME_PKG}" &> /dev/null
}

# Installs Google Chrome browser and creates a control script
# Downloads the latest stable Chrome .deb package, installs it with dpkg,
# fixes any dependency issues, and creates a browser control script at ~/.local/bin/browser
install_chrome() {
    check_can_sudo || return 1

    if chrome_is_installed; then
        echo "Google Chrome is already installed"
        install_browser_script
        return 0
    fi

    echo "Installing Google Chrome..."
    wget -O google-chrome-stable_current_amd64.deb "${DEB_URL}"
    sudo dpkg -i google-chrome-stable_current_amd64.deb || true
    sudo apt --fix-broken install -y
    rm -f google-chrome-stable_current_amd64.deb
    echo "Google Chrome installation completed"
    install_browser_script
}

install_browser_script() {
    if [ -x "${BROWSER_SCRIPT}" ]; then
        echo "Browser Script is already installed"
        return 0
    fi
    sudo mkdir -p "/usr/local/bin/"
    sudo tee "${BROWSER_SCRIPT}" <<'EOF' > /dev/null
#!/usr/bin/env bash
# Chrome Browser Control Script
# =============================
#
# This script provides functionality to control Google Chrome browser instances
# on Linux systems. It supports checking browser status, starting new instances,
# opening URLs in normal mode, and opening URLs in private (incognito) mode.
#
# Features:
# - Detects installed Chrome binary
# - Checks if Chrome is currently running
# - Starts Chrome in background (nohup)
# - Opens URLs in new tabs in existing or new Chrome instances
# - Supports private browsing (incognito), reusing existing incognito windows
#
# Usage:
#   browser                     → Print Chrome status
#   browser start               → Start Chrome (nohup)
#   browser open <URL>          → Open URL in new tab/window
#   browser private <URL>       → Open URL in incognito tab/window
#   browser kill                → Kill all Chrome instances
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2024. All rights reserved.
# Licensed under the MIT License.

get_browser_binary() {
  # Pick the best available Chrome binary and use it consistently
  BROWSER_BIN="$(command -v google-chrome-stable || command -v google-chrome || true)"

  if [ -z "${BROWSER_BIN}" ]; then
    echo "Google Chrome is not installed or not found in PATH." >&2
    return 1
  fi

  # Follow symlink and derive a good pgrep pattern
  local realpath basename pattern
  realpath="$(readlink -f "${BROWSER_BIN}" 2>/dev/null || echo "${BROWSER_BIN}")"
  basename="$(basename "${realpath}")"

  pattern="${basename}"
  # Optional: normalize the common 'stable' wrapper to the real binary name
  if [ "${pattern}" = "google-chrome-stable" ]; then
    pattern="google-chrome"
  fi

  BROWSER_PGREP_PATTERN="${pattern}"
  BROWSER_NAME="Chrome"
  export BROWSER_BIN
  export BROWSER_PGREP_PATTERN
  export BROWSER_NAME
}

check_running() {
  # Use -f so it matches anywhere in the command line
  pgrep -f "${BROWSER_PGREP_PATTERN}" >/dev/null 2>&1
}

print_status() {
  if check_running; then
    echo "${BROWSER_NAME} is running."
  else
    echo "${BROWSER_NAME} is NOT running."
  fi
}

start_browser() {
  if check_running; then
    echo "${BROWSER_NAME} is already running."
  else
    echo "Starting ${BROWSER_NAME} using ${BROWSER_BIN} ..."
    nohup "${BROWSER_BIN}" >/dev/null 2>&1 &
    sleep 1
    echo "${BROWSER_NAME} started."
  fi
}

kill_browser() {
  if check_running; then
    echo "Killing all ${BROWSER_NAME} instances..."
    pkill -f "${BROWSER_PGREP_PATTERN}"

    # Wait up to 5 seconds for processes to terminate
    # shellcheck disable=SC2034
    for i in {1..5}; do
      if ! check_running; then
        echo "${BROWSER_NAME} processes successfully terminated."
        return 0
      fi
      sleep 1
    done

    if check_running; then
      echo "WARNING: Some ${BROWSER_NAME} processes could not be terminated!"
      return 1
    fi
  else
    echo "No ${BROWSER_NAME} instances found running."
  fi
}

open_url() {
  local url="$1"
  if check_running; then
    echo "Opening URL in existing ${BROWSER_NAME} window..."
    "${BROWSER_BIN}" --new-tab "${url}" >/dev/null 2>&1 &
  else
    echo "${BROWSER_NAME} not running; starting with URL..."
    nohup "${BROWSER_BIN}" "${url}" >/dev/null 2>&1 &
    sleep 1
  fi
}

open_private_url() {
  local url="$1"
  # For Chrome, using --incognito will reuse any existing incognito profile;
  # if no incognito window exists, a new one is created.
  if check_running; then
    echo "Opening URL in existing ${BROWSER_NAME} incognito window..."
    "${BROWSER_BIN}" --incognito "${url}" >/dev/null 2>&1 &
  else
    echo "${BROWSER_NAME} not running; starting incognito with URL..."
    nohup "${BROWSER_BIN}" --incognito "${url}" >/dev/null 2>&1 &
    sleep 1
  fi
}

show_browser_usage() {
  local script_name
  script_name="$(basename "${BASH_SOURCE[0]}")"
  echo "Usage:"
  echo "  ${script_name}                     → Print Chrome status"
  echo "  ${script_name} start               → Start Chrome (nohup)"
  echo "  ${script_name} open <URL>          → Open URL in new tab/window"
  echo "  ${script_name} private <URL>       → Open URL in incognito tab/window"
  echo "  ${script_name} kill                → Kill all Chrome instances"
  echo "  ${script_name} help | -h           → Show this help"
}

### MAIN LOGIC ###
browser_main() {
  get_browser_binary || return 1

  case $# in
    0)  # No arguments → print status
      print_status
      show_browser_usage
      return 0
      ;;
    1)  # One argument: start | kill | help | -h
      case $1 in
        "start")  # Ensure Chrome browser is running, start if not already running
          start_browser
          return 0
          ;;
        "kill")   # Kill all Chrome instances
          kill_browser
          return 0
          ;;
        "help" | "-h")  # Show usage help
          show_browser_usage
          return 0
          ;;
        *)      # Invalid argument
          show_browser_usage
          return 1
          ;;
      esac
      ;;
    2)  # Two arguments: open URL | private URL
      case $1 in
        "open")   # Open URL in normal Chrome session
          open_url "$2"
          return 0
          ;;
        "private") # Open URL in incognito, reusing existing incognito window if any
          open_private_url "$2"
          return 0
          ;;
        *)      # Invalid first argument
          show_browser_usage
          return 1
          ;;
      esac
      ;;
    *)  # Invalid number of arguments
      show_browser_usage
      return 1
      ;;
  esac
}

# Export functions when script is sourced
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  get_browser_binary 2>/dev/null || true
  export -f get_browser_binary
  export -f check_running
  export -f print_status
  export -f start_browser
  export -f kill_browser
  export -f open_url
  export -f open_private_url
  export -f show_browser_usage
  export -f browser_main
  return 0
else
  # Execute browser_main() if script is run directly
  browser_main "$@"
fi
EOF
    sudo chmod +x "${BROWSER_SCRIPT}"
    echo "Browser start/stop script installed at ${BROWSER_SCRIPT}"
}

# Uninstalls Google Chrome browser and removes configuration
# Removes the Chrome package, user configuration files, and the browser control script
# Note: User configuration removal can be disabled by commenting out that section
uninstall_chrome() {
    check_can_sudo || return 1

    if ! chrome_is_installed; then
        echo "Google Chrome (${CHROME_PKG}) does not appear to be installed"
    else
        echo "Uninstalling Google Chrome..."
        sudo apt --purge remove -y "${CHROME_PKG}"
        sudo apt autoremove -y
        echo "Google Chrome package removed"
    fi

    if [ -f "${BROWSER_SCRIPT}" ]; then
        echo "Removing browser start/stop script from ${BROWSER_SCRIPT}"
        sudo rm -f "${BROWSER_SCRIPT}"
    fi

    if [ -d "$HOME/.config/google-chrome" ]; then
        read -r -p "Remove Google Chrome user configuration (~/.config/google-chrome)? [y/N] " reply
        if [[ "${reply}" =~ ^[Yy]$ ]]; then
            echo "Removing Google Chrome user configuration under ~/.config/google-chrome"
            rm -rf "$HOME/.config/google-chrome"
        else
            echo "Keeping Google Chrome user configuration"
        fi
    fi

    echo "Google Chrome uninstallation completed"
}

# Main execution
# Defaults to 'install' if no argument provided
ACTION="${1:-install}"

case "${ACTION}" in
    install)
        install_chrome
        ;;
    uninstall)
        uninstall_chrome
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "Unknown action: ${ACTION}"
        usage
        exit 1
        ;;
esac
