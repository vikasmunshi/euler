#!/usr/bin/env bash
###############################################################################
# Script Name:    setup_pycharm_service.sh
# Description:    Install the PyCharm wrapper script and systemd user service.
#
# What it does:
#   - Creates ~/.local/bin/pycharm (manager script)
#   - Creates ~/.local/bin/pycharm-service-launcher (used by systemd)
#   - Creates ~/.config/systemd/user/pycharm.service
#   - Reloads systemd user units
#   - Enables and starts pycharm.service for the current user
#
# Requirements:
#   - systemd user services enabled (`systemctl --user` works)
#   - PyCharm installed at $HOME/.local/pycharm/bin/pycharm
#
# Author:         Vikas Munshi <vikas.munshi@gmail.com>
# License:        MIT License
###############################################################################

set -euo pipefail

PYCHARM_WRAPPER="$HOME/.local/bin/pycharm"
PYCHARM_LAUNCHER="$HOME/.local/bin/pycharm-service-launcher"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
SERVICE_NAME="pycharm.service"

echo "==> Creating ~/.local/bin directory (if needed)..."
mkdir -p "$(dirname "$PYCHARM_WRAPPER")"

###############################################################################
# 1. Install the PyCharm manager script (~/.local/bin/pycharm)
###############################################################################
echo "==> Installing PyCharm manager script to $PYCHARM_WRAPPER..."
cat <<'PYCHARM_SCRIPT' > "$PYCHARM_WRAPPER"
#!/bin/bash
###############################################################################
# Script Name:    pycharm
# Description:    Manage PyCharm IDE as a standalone application or as a
#                 systemd user service. Supports status, start, stop, and kill.
#
# Usage:          pycharm [start|stop|kill|service]
#                 Options:
#                   -h, --help     Show this help
#                       --no-color  Disable ANSI colours
#                 Examples:
#                   pycharm
#                   pycharm start
#                   pycharm service
#                   pycharm --no-color stop
#
# Requirements:   - systemd user services enabled
#                 - PyCharm installed at $HOME/.local/pycharm/bin/pycharm
#
# Author:         Vikas Munshi <vikas.munshi@gmail.com>
# License:        MIT License
# Version:        1.1
###############################################################################

set -u

# ---------------------- Configuration ----------------------
# Path to PyCharm executable
PYCHARM_BIN="$HOME/.local/pycharm/bin/pycharm"
# Name of the systemd service
SERVICE_NAME="pycharm.service"

# ---------------------- Colour Handling --------------------
# Honour NO_COLOR standard and --no-color flag, and disable when stdout is not a TTY.
USE_COLOR=true
for arg in "$@"; do
  if [[ "$arg" == "--no-color" ]]; then USE_COLOR=false; break; fi
done
if [[ -n "${NO_COLOR:-}" || ! -t 1 ]]; then USE_COLOR=false; fi

if $USE_COLOR; then
  if command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
    BOLD="$(tput bold)"; RESET="$(tput sgr0)"
    RED="$(tput setaf 1)"; GREEN="$(tput setaf 2)"; YELLOW="$(tput setaf 3)"
    BLUE="$(tput setaf 4)"; MAGENTA="$(tput setaf 5)"; CYAN="$(tput setaf 6)"; GREY="$(tput setaf 8)"
  else
    BOLD=""; RESET=$'\e[0m'
    RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'
    BLUE=$'\e[34m'; MAGENTA=$'\e[35m'; CYAN=$'\e[36m'; GREY=$'\e[90m'
  fi
else
  RED=""; GREEN=""; YELLOW=""; BLUE=""; MAGENTA=""; CYAN=""; GREY=""; BOLD=""; RESET=""
fi

info()    { printf "%b[INFO]%b %s\n"    "$CYAN"   "$RESET" "$*"; }
success() { printf "%b[SUCCESS]%b %s\n" "$GREEN"  "$RESET" "$*"; }
warn()    { printf "%b[WARN]%b %s\n"    "$YELLOW" "$RESET" "$*"; }
error()   { printf "%b[ERROR]%b %s\n"   "$RED"    "$RESET" "$*"; }

# ---------------------- Helpers ----------------------------

usage() {
  cat <<EOF
${BOLD}Usage${RESET}: $(basename "$0") [start|stop|kill|service]
Options:
  -h, --help      Show this help
      --no-color  Disable ANSI colours
No argument shows current PyCharm status.
EOF
}

# Check if the PyCharm process is running (standalone or service)
check_if_running() {
  pgrep -f -- "$PYCHARM_BIN" >/dev/null
}

# Check if the PyCharm systemd service is active
check_service_active() {
  systemctl --user is-active --quiet "$SERVICE_NAME"
}

# Determine if PyCharm is running as a service
is_running_as_service() {
  if check_if_running && check_service_active; then
    return 0
  else
    return 1
  fi
}

# Show a one-line status
show_status() {
  if check_if_running; then
    if check_service_active; then
      success "PyCharm process is running, started as ${BOLD}service${RESET}."
    else
      success "PyCharm process is running, started as ${BOLD}standalone${RESET}."
    fi
  else
    warn "PyCharm process is not running."
  fi
}

# Confirm with user before destructive actions
confirm() {
  local prompt
  prompt="$(printf "%s%s%s [y/N]: " "$YELLOW" "$1" "$RESET")"
  read -r -p "$prompt" response
  [[ "$response" =~ ^[Yy]$ ]]
}

# ---------------------- Argument Parsing -------------------
# Strip known flags first so command can be in any position, e.g. "--no-color start"
ARGS=()
for a in "$@"; do
  case "$a" in
    -h|--help) usage; exit 0 ;;
    --no-color) ;; # already handled
    *) ARGS+=("$a") ;;
  esac
done
command="${ARGS[0]:-}"

# ---------------------- Main Script Logic ------------------

case "${command}" in
  "")
    show_status
    ;;
  start)
    if check_if_running; then
      warn "PyCharm is already running."
    else
      info "Starting PyCharm in standalone mode..."
      nohup "$PYCHARM_BIN" >/dev/null 2>&1 &
      # Brief grace period then report status
      sleep 0.5
      if check_if_running; then
        success "PyCharm started (standalone)."
      else
        error "Failed to start PyCharm. Check the binary path: $PYCHARM_BIN"
      fi
    fi
    ;;
  service)
    if check_if_running || check_service_active; then
      warn "PyCharm is already running."
    else
      info "Starting PyCharm as a systemd user service..."
      if systemctl --user start "$SERVICE_NAME"; then
        # Give systemd a moment to settle
        sleep 0.5
        if check_service_active; then
          success "PyCharm service started."
        else
          error "Service start issued but not active. Run: systemctl --user status $SERVICE_NAME"
        fi
      else
        error "Failed to start service. Run: systemctl --user status $SERVICE_NAME"
      fi
    fi
    ;;
  stop)
    if check_service_active; then
      info "Stopping PyCharm service..."
      if systemctl --user stop "$SERVICE_NAME"; then
        sleep 0.5
        if check_service_active; then
          warn "Service still reported active. Inspect: systemctl --user status $SERVICE_NAME"
        else
          success "PyCharm service stopped."
        fi
      else
        error "Failed to stop service. Inspect: systemctl --user status $SERVICE_NAME"
      fi
    elif check_if_running; then
      warn "PyCharm is running in standalone mode."
      info "Please close the application window to stop it."
    else
      warn "PyCharm is not running."
    fi
    ;;
  kill)
    if check_service_active; then
      info "Stopping PyCharm service..."
      if systemctl --user stop "$SERVICE_NAME"; then
        sleep 0.5
        if check_service_active; then
          warn "Service still reported active. Inspect: systemctl --user status $SERVICE_NAME"
        else
          success "PyCharm service stopped."
        fi
      else
        error "Failed to stop service. Inspect: systemctl --user status $SERVICE_NAME"
      fi
    elif check_if_running; then
      if confirm "Are you sure you want to force-kill the standalone PyCharm process?"; then
        warn "Sending SIGKILL to PyCharm process."
        if pkill -9 -f -- "$PYCHARM_BIN"; then
          sleep 0.5
          if check_if_running; then
            error "PyCharm still running after kill attempt."
          else
            success "PyCharm process terminated."
          fi
        else
          error "No matching PyCharm process found to kill."
        fi
      else
        info "Kill aborted."
      fi
    else
      warn "PyCharm is not running."
    fi
    ;;
  *)
    error "Unknown command: ${command}"
    usage
    exit 1
    ;;
esac
PYCHARM_SCRIPT

chmod +x "$PYCHARM_WRAPPER"
echo "==> Manager script installed."

###############################################################################
# 2. Install the systemd launcher script (~/.local/bin/pycharm-service-launcher)
###############################################################################
echo "==> Installing PyCharm systemd launcher to $PYCHARM_LAUNCHER..."
cat <<'LAUNCHER_SCRIPT' > "$PYCHARM_LAUNCHER"
#!/usr/bin/env bash
# Launcher used *only* by systemd user service.
set -euo pipefail

export DISPLAY="${DISPLAY:-:0}"
PYCHARM="$HOME/.local/pycharm/bin/pycharm"

if [ ! -x "$PYCHARM" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: PyCharm not found at $PYCHARM" >&2
    exit 1
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') Starting PyCharm (systemd service)..."
exec "$PYCHARM"
LAUNCHER_SCRIPT

chmod +x "$PYCHARM_LAUNCHER"
echo "==> Launcher script installed."

###############################################################################
# 3. Install systemd user unit (~/.config/systemd/user/pycharm.service)
###############################################################################
echo "==> Creating systemd user directory (if needed)..."
mkdir -p "$SYSTEMD_USER_DIR"

SERVICE_FILE="$SYSTEMD_USER_DIR/$SERVICE_NAME"

echo "==> Installing systemd user service to $SERVICE_FILE..."
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=PyCharm IDE (user service)
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/bin/pycharm-service-launcher
Restart=on-failure

[Install]
WantedBy=default.target
EOF

###############################################################################
# 4. Reload, enable, start
###############################################################################
echo "==> Reloading systemd user units..."
systemctl --user daemon-reload

echo "==> Enabling and starting $SERVICE_NAME..."
systemctl --user enable --now "$SERVICE_NAME"

echo "==> Done."
echo "You can now use the 'pycharm' command to manage the IDE:"
echo "  pycharm           # show status"
echo "  pycharm service   # start via systemd user service"
echo "  pycharm start     # start standalone"
echo "  pycharm stop      # stop service"
echo "  pycharm kill      # kill standalone process"
