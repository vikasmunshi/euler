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
BROWSER_COMPLETION="/etc/bash_completion.d/browser"

usage() {
    echo "Usage: $0 [install|uninstall]"
    echo
    echo "  install         Install Google Chrome (default if no argument given)"
    echo "  install-script  Install browser start/stop script"
    echo "  install-completion  Install bash completion for the browser command"
    echo "  uninstall       Remove Google Chrome and its configuration"
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
        return 0
    fi

    echo "Installing Google Chrome..."
    wget -O google-chrome-stable_current_amd64.deb "${DEB_URL}"
    sudo dpkg -i google-chrome-stable_current_amd64.deb || true
    sudo apt --fix-broken install -y
    rm -f google-chrome-stable_current_amd64.deb
    echo "Google Chrome installation completed"
    install_browser_script
    browser start
}

install_browser_script() {
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
# - Refreshes and focuses the existing tab when the URL is already open
# - Named tabs: open-in-tab reuses (refreshes or navigates) the tab registered under a name
# - Supports private browsing (incognito), reusing existing incognito windows
#
# Usage:
#   browser                            → Print Chrome status
#   browser start                      → Start Chrome (nohup)
#   browser open <URL>                 → Open URL in new tab/window
#   browser open-in-tab <NAME> <URL>   → Open URL in the named tab, reusing it if open
#   browser private <URL>              → Open URL in incognito tab/window
#   browser kill                       → Kill all Chrome instances
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
  BROWSER_DEBUG_PORT=9222
  BROWSER_DEBUG_DIR="${HOME}/.config/google-chrome-browser"
  BROWSER_NAMED_TABS="${BROWSER_DEBUG_DIR}/named-tabs"
  export BROWSER_BIN
  export BROWSER_PGREP_PATTERN
  export BROWSER_NAME
  export BROWSER_DEBUG_PORT
  export BROWSER_DEBUG_DIR
  export BROWSER_NAMED_TABS
}

check_running() {
  # "Running" means *our* managed instance (the one launched with the remote
  # debugging port and the dedicated user-data-dir) is up and reachable, not
  # just any chrome process. This is what lets us open tabs into it reliably;
  # a plain pgrep would also match the user's normal-profile Chrome, against
  # which our --user-data-dir launch would spawn a separate window.
  if command -v curl >/dev/null 2>&1; then
    curl -sf --max-time 1 "http://localhost:${BROWSER_DEBUG_PORT}/json/version" \
      >/dev/null 2>&1 && return 0
    return 1
  fi
  # No curl: fall back to a best-effort process match.
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
    nohup "${BROWSER_BIN}" "--remote-debugging-port=${BROWSER_DEBUG_PORT}" "--user-data-dir=${BROWSER_DEBUG_DIR}" >/dev/null 2>&1 &
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

# Canonicalise a URL/path for comparison so that the value we were asked to
# open lines up with what Chrome actually stores. Chrome appends a trailing
# slash to bare origins (https://example.com -> https://example.com/) and keeps
# #fragments, which is exactly why a naive substring match kept missing and
# re-opening duplicate tabs.
normalize_url() {
  local u="$1"
  # Local paths -> file:// URLs
  if [[ "${u}" != *://* ]]; then
    u="file://$(realpath "${u}" 2>/dev/null || printf '%s' "${u}")"
  fi
  u="${u%%#*}"   # drop any #fragment
  u="${u%/}"     # drop a single trailing slash
  printf '%s' "${u}"
}

# Emit one currently-open tab URL per line via the DevTools JSON endpoint.
# Matching on the exact "url": key avoids the faviconUrl / devtoolsFrontendUrl
# / webSocketDebuggerUrl fields (whose key has an uppercase "Url").
list_open_tab_urls() {
  command -v curl >/dev/null 2>&1 || return 1
  curl -sf --max-time 1 "http://localhost:${BROWSER_DEBUG_PORT}/json" 2>/dev/null \
    | grep -oE '"url":[[:space:]]*"[^"]*"' \
    | sed -E 's/^"url":[[:space:]]*"(.*)"$/\1/'
}

url_is_already_open() {
  local want u
  want="$(normalize_url "$1")"
  while IFS= read -r u; do
    [ -n "${u}" ] || continue
    if [ "$(normalize_url "${u}")" = "${want}" ]; then
      return 0
    fi
  done < <(list_open_tab_urls)
  return 1
}

# Print the DevTools target id of the first open tab whose URL matches $1 (after
# normalisation), or nothing. Chrome's /json output is pretty-printed one field
# per line, and within each target object the "id" field precedes "url", so we
# remember the most recent id and emit it as soon as a matching url turns up.
# Only the lowercase "url" key matches (faviconUrl/webSocketDebuggerUrl/etc. all
# capitalise the U), which is the same trick list_open_tab_urls relies on.
find_open_tab_id() {
  command -v curl >/dev/null 2>&1 || return 1
  local want line id="" url
  want="$(normalize_url "$1")"
  while IFS= read -r line; do
    case "${line}" in
      *'"id":'*)
        id="$(printf '%s' "${line}" | sed -E 's/.*"id":[[:space:]]*"([^"]*)".*/\1/')"
        ;;
      *'"url":'*)
        url="$(printf '%s' "${line}" | sed -E 's/.*"url":[[:space:]]*"([^"]*)".*/\1/')"
        if [ "$(normalize_url "${url}")" = "${want}" ]; then
          printf '%s' "${id}"
          return 0
        fi
        ;;
    esac
  done < <(curl -sf --max-time 1 "http://localhost:${BROWSER_DEBUG_PORT}/json" 2>/dev/null)
  return 1
}

# Print the current URL of the tab whose DevTools target id is $1, relying on
# the same id-precedes-url line pairing as find_open_tab_id.
get_tab_url() {
  command -v curl >/dev/null 2>&1 || return 1
  local want="$1" line id=""
  while IFS= read -r line; do
    case "${line}" in
      *'"id":'*)
        id="$(printf '%s' "${line}" | sed -E 's/.*"id":[[:space:]]*"([^"]*)".*/\1/')"
        ;;
      *'"url":'*)
        if [ "${id}" = "${want}" ]; then
          printf '%s' "${line}" | sed -E 's/.*"url":[[:space:]]*"([^"]*)".*/\1/'
          return 0
        fi
        ;;
    esac
  done < <(curl -sf --max-time 1 "http://localhost:${BROWSER_DEBUG_PORT}/json" 2>/dev/null)
  return 1
}

# True if a DevTools target with id $1 is currently open.
tab_id_is_open() {
  command -v curl >/dev/null 2>&1 || return 1
  curl -sf --max-time 1 "http://localhost:${BROWSER_DEBUG_PORT}/json" 2>/dev/null \
    | grep -qE "\"id\":[[:space:]]*\"$1\""
}

# Wait for the DevTools endpoint to answer, polling for at most $1 (default 10)
# seconds. A cold Chrome start needs a few seconds before /json is reachable.
wait_for_devtools() {
  local deadline=$(( SECONDS + ${1:-10} ))
  while (( SECONDS < deadline )); do
    check_running && return 0
    sleep 0.25
  done
  return 1
}

# Print the target id of the only open "page" tab; fail when there are none or
# several. ("page" targets exclude extension background pages and workers; the
# id field precedes type in each /json object, as in find_open_tab_id.)
sole_page_tab_id() {
  command -v curl >/dev/null 2>&1 || return 1
  local line id="" found="" count=0
  while IFS= read -r line; do
    case "${line}" in
      *'"id":'*)
        id="$(printf '%s' "${line}" | sed -E 's/.*"id":[[:space:]]*"([^"]*)".*/\1/')"
        ;;
      *'"type":'*'"page"'*)
        found="${id}"
        count=$((count + 1))
        ;;
    esac
  done < <(curl -sf --max-time 1 "http://localhost:${BROWSER_DEBUG_PORT}/json" 2>/dev/null)
  [ "${count}" -eq 1 ] && [ -n "${found}" ] && printf '%s' "${found}"
}

# The named-tab registry maps a caller-chosen tab name to the DevTools target
# id it last resolved to, one "name<TAB>id" line per name. Target ids die with
# their tab (and with the browser), so callers must validate an id with
# tab_id_is_open before trusting it, and re-register when it has gone stale.
get_named_tab_id() {
  local name="$1" id
  [ -f "${BROWSER_NAMED_TABS}" ] || return 1
  id="$(awk -F '\t' -v n="${name}" '$1 == n { print $2; exit }' "${BROWSER_NAMED_TABS}")"
  [ -n "${id}" ] || return 1
  printf '%s' "${id}"
}

set_named_tab_id() {
  local name="$1" id="$2" tmp
  mkdir -p "$(dirname "${BROWSER_NAMED_TABS}")"
  tmp="$(mktemp)"
  if [ -f "${BROWSER_NAMED_TABS}" ]; then
    awk -F '\t' -v n="${name}" '$1 != n' "${BROWSER_NAMED_TABS}" > "${tmp}"
  fi
  printf '%s\t%s\n' "${name}" "${id}" >> "${tmp}"
  mv "${tmp}" "${BROWSER_NAMED_TABS}"
}

# Send a single DevTools protocol command to a tab over its WebSocket. Chrome
# only exposes reload and navigate through the protocol (the /json HTTP
# endpoints can create, activate and close tabs but never drive one), so we
# speak just enough of the WebSocket wire format by hand: an HTTP/1.1 Upgrade
# handshake over a raw TCP connection, followed by a single masked text frame
# carrying the JSON command. The mask is all-zero, which RFC 6455 permits and
# which lets us write the payload bytes unchanged. Returns non-zero if the
# socket or handshake fails.
ws_send() {
  local id="$1"
  local payload="$2"
  local host="localhost"
  local key len line
  exec 3<>"/dev/tcp/${host}/${BROWSER_DEBUG_PORT}" 2>/dev/null || return 1
  key="$(head -c 16 /dev/urandom | base64)"
  printf 'GET /devtools/page/%s HTTP/1.1\r\nHost: %s:%s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' \
    "${id}" "${host}" "${BROWSER_DEBUG_PORT}" "${key}" >&3
  # Drain the handshake response up to its blank line; bail on EOF/timeout so we
  # never hang on a connection that did not upgrade.
  while IFS= read -r -t 2 line <&3; do
    line="${line%$'\r'}"
    [ -z "${line}" ] && break
  done
  # FIN + text opcode (0x81); MASK bit set alongside the length. Payloads up to
  # 125 bytes fit in the 7-bit length; longer ones (a navigate carrying a long
  # URL) use the 126 marker followed by a 16-bit big-endian byte count.
  len="$(printf '%s' "${payload}" | wc -c)"
  printf '\x81' >&3
  if [ "${len}" -lt 126 ]; then
    printf "\\x$(printf '%02x' $((0x80 | len)))" >&3
  else
    printf '\xfe' >&3
    printf "\\x$(printf '%02x' $((len >> 8)))\\x$(printf '%02x' $((len & 0xff)))" >&3
  fi
  printf '\x00\x00\x00\x00' >&3
  printf '%s' "${payload}" >&3
  exec 3>&-
  return 0
}

ws_reload() {
  ws_send "$1" '{"id":1,"method":"Page.reload"}'
}

# Point an existing tab at a new URL via Page.navigate. Bare local paths become
# file:// URLs (Page.navigate resolves nothing itself); backslashes and quotes
# are escaped so the URL embeds safely in the JSON command.
ws_navigate() {
  local id="$1"
  local url="$2"
  if [[ "${url}" != *://* ]]; then
    url="file://$(realpath "${url}" 2>/dev/null || printf '%s' "${url}")"
  fi
  url="${url//\\/\\\\}"
  url="${url//\"/\\\"}"
  ws_send "${id}" "{\"id\":1,\"method\":\"Page.navigate\",\"params\":{\"url\":\"${url}\"}}"
}

# Bring an already-open tab to the foreground (best effort, via the HTTP
# activate endpoint) and refresh it over the WebSocket. Returns ws_reload's
# status so the caller can fall back to a plain "already open" message.
reload_open_tab() {
  local id="$1"
  local no_refresh="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -sf --max-time 2 "http://localhost:${BROWSER_DEBUG_PORT}/json/activate/${id}" >/dev/null 2>&1 || true
  fi
  [[ -z "${no_refresh}" ]] && ws_reload "${id}"
}

# Open a URL as a new *tab* in the running managed instance. Going through the
# DevTools /json/new endpoint always creates a tab inside the existing browser
# (never a separate window), which is the behaviour the binary's non-existent
# --new-tab switch only pretended to provide. Newer Chrome requires PUT; we try
# PUT, then GET (older builds), then fall back to handing the URL to the binary.
open_url_in_new_tab() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    if curl -sf --max-time 2 -X PUT \
         "http://localhost:${BROWSER_DEBUG_PORT}/json/new?${url}" >/dev/null 2>&1; then
      return 0
    fi
    if curl -sf --max-time 2 \
         "http://localhost:${BROWSER_DEBUG_PORT}/json/new?${url}" >/dev/null 2>&1; then
      return 0
    fi
  fi
  # Fallback: a bare URL handed to the running instance opens in a new tab of
  # the most recently focused window.
  "${BROWSER_BIN}" "--user-data-dir=${BROWSER_DEBUG_DIR}" "${url}" >/dev/null 2>&1 &
}

# Create a new tab for $1 via /json/new and print the new target's id (PUT for
# newer Chrome, GET for older builds). Unlike open_url_in_new_tab there is no
# binary fallback: callers need the id, and a launch via the binary never
# reports one.
new_tab_with_id() {
  command -v curl >/dev/null 2>&1 || return 1
  local url="$1" out id
  out="$(curl -sf --max-time 2 -X PUT "http://localhost:${BROWSER_DEBUG_PORT}/json/new?${url}" 2>/dev/null)" \
    || out="$(curl -sf --max-time 2 "http://localhost:${BROWSER_DEBUG_PORT}/json/new?${url}" 2>/dev/null)" \
    || return 1
  id="$(printf '%s' "${out}" | grep -oE '"id":[[:space:]]*"[^"]*"' | head -n 1 | sed -E 's/.*"([^"]*)".*/\1/')"
  [ -n "${id}" ] || return 1
  printf '%s' "${id}"
}

open_url() {
  local url="$1"
  local no_refresh="$2"
  if ! check_running; then
    echo "${BROWSER_NAME} not running; starting with URL..."
    nohup "${BROWSER_BIN}" "--remote-debugging-port=${BROWSER_DEBUG_PORT}" "--user-data-dir=${BROWSER_DEBUG_DIR}" "${url}" >/dev/null 2>&1 &
    sleep 1
  elif url_is_already_open "${url}"; then
    local tab_id
    tab_id="$(find_open_tab_id "${url}")"
    if [ -n "${tab_id}" ] && reload_open_tab "${tab_id}" "${no_refresh}"; then
      [[ -z "${no_refresh}" ]] && {
        echo "URL ${url} already open in ${BROWSER_NAME}; focused the existing tab and refreshed."
      } || {
        echo "URL ${url} already open in ${BROWSER_NAME}; focused the existing tab."
      }
    else
      echo "URL ${url} is already open in ${BROWSER_NAME}; not opening a duplicate."
    fi
  else
    echo "Opening URL in a new tab in the existing ${BROWSER_NAME} window..."
    open_url_in_new_tab "${url}"
  fi
}

# Open a URL in the tab registered under a caller-chosen name, reusing that
# tab whenever it is still open: same URL → focus + refresh, different URL →
# navigate the tab in place. Otherwise (unknown name, or its tab or browser
# has since closed) a fresh tab is created and recorded under the name.
open_url_in_named_tab() {
  local name="$1"
  local url="$2"
  local id
  if ! check_running; then
    echo "${BROWSER_NAME} not running; starting with URL..."
    nohup "${BROWSER_BIN}" "--remote-debugging-port=${BROWSER_DEBUG_PORT}" "--user-data-dir=${BROWSER_DEBUG_DIR}" "${url}" >/dev/null 2>&1 &
    # Register the tab Chrome opened for the URL: wait for DevTools to come up
    # (a cold start needs a few seconds), then find the tab by URL — or, when
    # the page has already redirected (e.g. to a login page), settle for the
    # only page tab there is. Skipping this would strand the tab unregistered
    # and make every later call open a duplicate.
    if wait_for_devtools 15; then
      id="$(find_open_tab_id "${url}")" || id="$(sole_page_tab_id)" || id=""
      [ -n "${id}" ] && set_named_tab_id "${name}" "${id}"
    fi
    return 0
  fi
  id="$(get_named_tab_id "${name}")" || id=""
  if [ -n "${id}" ] && tab_id_is_open "${id}"; then
    if [ "$(normalize_url "$(get_tab_url "${id}")")" = "$(normalize_url "${url}")" ]; then
      echo "Tab '${name}' already shows ${url}; focused and refreshed it."
      reload_open_tab "${id}" ""
    else
      echo "Reusing tab '${name}' for ${url}..."
      if command -v curl >/dev/null 2>&1; then
        curl -sf --max-time 2 "http://localhost:${BROWSER_DEBUG_PORT}/json/activate/${id}" >/dev/null 2>&1 || true
      fi
      ws_navigate "${id}" "${url}"
    fi
  elif id="$(find_open_tab_id "${url}")" && [ -n "${id}" ]; then
    # The name is unregistered (or its tab is gone) but some tab already shows
    # the URL — adopt it rather than opening a duplicate.
    echo "Adopting the open ${url} tab as '${name}'; focused and refreshed it."
    set_named_tab_id "${name}" "${id}"
    reload_open_tab "${id}" ""
  else
    echo "Opening URL in new tab '${name}'..."
    if id="$(new_tab_with_id "${url}")"; then
      set_named_tab_id "${name}" "${id}"
    else
      # No id to register (no curl / DevTools refused) — still open the URL.
      open_url_in_new_tab "${url}"
    fi
  fi
}

open_private_url() {
  local url="$1"
  # For Chrome, using --incognito will reuse any existing incognito profile;
  # if no incognito window exists, a new one is created.
  if check_running; then
    echo "Opening URL in existing ${BROWSER_NAME} incognito window..."
    "${BROWSER_BIN}" --incognito "--user-data-dir=${BROWSER_DEBUG_DIR}" "${url}" >/dev/null 2>&1 &
  else
    echo "${BROWSER_NAME} not running; starting incognito with URL..."
    nohup "${BROWSER_BIN}" "--remote-debugging-port=${BROWSER_DEBUG_PORT}" "--user-data-dir=${BROWSER_DEBUG_DIR}" --incognito "${url}" >/dev/null 2>&1 &
    sleep 1
  fi
}

show_browser_usage() {
  local script_name
  script_name="$(basename "${BASH_SOURCE[0]}")"
  echo "Usage:"
  echo "  ${script_name}                            → Print Chrome status"
  echo "  ${script_name} start                      → Start Chrome (nohup)"
  echo "  ${script_name} open <URL>                 → Open URL in new tab/refresh existing tab with url open"
  echo "  ${script_name} open <URL> --no-refresh    → Open URL in new tab/activate existing tab with url open"
  echo "  ${script_name} open-in-tab <name> <URL>   → Open URL in the named tab, reusing/navigating it if open"
  echo "  ${script_name} private <URL>              → Open URL in incognito tab/window"
  echo "  ${script_name} kill                       → Kill all Chrome instances"
  echo "  ${script_name} help | -h                  → Show this help"
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
    2 | 3)  # Two or three arguments: open URL [--no-refresh] | open-in-tab NAME URL | private URL
      case $1 in
        "open")   # Open URL in normal Chrome session
          local no_refresh=""
          if [ "${3:-}" = "--no-refresh" ]; then
            no_refresh="--no-refresh"
          fi
          open_url "$2" "${no_refresh}"
          return 0
          ;;
        "open-in-tab")  # Open URL in a named tab, creating or reusing it
          if [ $# -ne 3 ]; then
            show_browser_usage
            return 1
          fi
          open_url_in_named_tab "$2" "$3"
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
  export -f normalize_url
  export -f list_open_tab_urls
  export -f url_is_already_open
  export -f find_open_tab_id
  export -f get_tab_url
  export -f tab_id_is_open
  export -f wait_for_devtools
  export -f sole_page_tab_id
  export -f get_named_tab_id
  export -f set_named_tab_id
  export -f ws_send
  export -f ws_reload
  export -f ws_navigate
  export -f reload_open_tab
  export -f open_url_in_new_tab
  export -f new_tab_with_id
  export -f open_url
  export -f open_url_in_named_tab
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
    install_browser_completion
}

install_browser_completion() {
    # Always (re)write so completion updates land alongside script updates.
    sudo tee "${BROWSER_COMPLETION}" <<'EOF' > /dev/null
# Bash completion for the browser command
_browser_completions() {
  local cur prev
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  case "${COMP_CWORD}" in
    1)
      COMPREPLY=($(compgen -W "start kill open open-in-tab private help -h" -- "${cur}"))
      ;;
    2)
      case "${prev}" in
        open|private)
          COMPREPLY=($(compgen -f -- "${cur}"))
          ;;
        open-in-tab)
          # Offer the already-registered tab names
          local named_tabs="${HOME}/.config/google-chrome-browser/named-tabs"
          if [ -f "${named_tabs}" ]; then
            COMPREPLY=($(compgen -W "$(cut -f1 "${named_tabs}")" -- "${cur}"))
          fi
          ;;
      esac
      ;;
    3)
      case "${COMP_WORDS[1]}" in
        open)
          COMPREPLY=($(compgen -W "--no-refresh" -- "${cur}"))
          ;;
        open-in-tab)
          COMPREPLY=($(compgen -f -- "${cur}"))
          ;;
      esac
      ;;
  esac
}
complete -F _browser_completions browser
EOF
    echo "Browser completion installed at ${BROWSER_COMPLETION}"
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

    if [ -f "${BROWSER_COMPLETION}" ]; then
        echo "Removing browser completion from ${BROWSER_COMPLETION}"
        sudo rm -f "${BROWSER_COMPLETION}"
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
    install-script)
        install_browser_script
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
