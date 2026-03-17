#!/usr/bin/env bash
# System Upgrade Service Setup Script (Revised v5)
# -----------------------------------------------------------------------------
# This script automates the installation and configuration of a systemd-based
# automatic system upgrade service. It creates necessary system files and
# configures a daily upgrade timer to keep the system updated.
#
# Features:
# - Creates system upgrade script with proper error handling and logging
# - Uses set -Eeuo pipefail for strict error handling
# - Captures full apt-get output to temporary files for analysis
# - Extracts and logs both summary statistics and package details
# - Sets up systemd service and timer units
# - Configures daily upgrades at 08:00 with 30-minute randomized delay
# - Runs only once per day (tracks via timestamp file)
# - Uses flock-based locking to prevent concurrent runs
# - Recovers interrupted packages with dpkg --configure -a before upgrading
# - Provides uninstall capability to cleanly remove all components
# - Debug mode via DEBUG=1 environment variable
# - Cleans up packages with apt-get autoremove and apt-get clean
# - Creates status-jobs command for quick service status checks
#
# Usage:
#   sudo ./setup_upgrade_service.sh              → Install/setup upgrade service
#   sudo ./setup_upgrade_service.sh --uninstall  → Remove upgrade service
#   sudo DEBUG=1 systemctl start upgrade.service → Test with tracing
#
# Files created:
#   - /usr/local/bin/upgrade.sh                  → Upgrade script
#   - /etc/systemd/system/upgrade.service        → Systemd service unit
#   - /etc/systemd/system/upgrade.timer          → Systemd timer unit
#   - /usr/local/bin/status-jobs                 → Status check script
#   - /var/log/upgrade.log                       → Upgrade log file
#   - /var/lib/upgrade/last_upgrade_check        → Last run timestamp (644)
#   - /run/upgrade/upgrade.lock                  → Runtime lock file
#
# Timer Configuration:
# - OnCalendar=*-*-* 08:00:00 : Runs daily at 08:00
# - RandomizedDelaySec=30m    : Random 0-30 minute delay
# - Persistent=true           : Catches up missed runs after boot
#
# Service Configuration:
# - Type=oneshot              : Runs once and exits
# - Nice=10                   : Low CPU priority
# - IOSchedulingClass=best-effort, IOSchedulingPriority=7 : Low I/O priority
#
# Troubleshooting:
#   systemctl list-timers upgrade.timer    → Check next scheduled run
#   journalctl -u upgrade.service          → View service logs
#   tail -f /var/log/upgrade.log           → Monitor upgrade log
#   cat /var/lib/upgrade/last_upgrade_check → Check last run date
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# License: MIT
# Version: 5.0
# -----------------------------------------------------------------------------

set -Eeuo pipefail

SCRIPT_PATH="/usr/local/bin/upgrade.sh"
SERVICE_PATH="/etc/systemd/system/upgrade.service"
TIMER_PATH="/etc/systemd/system/upgrade.timer"
STATUS_PATH="/usr/local/bin/status-jobs"
LOG_FILE="/var/log/upgrade.log"

require_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "[ERROR] Please run as root (e.g., sudo $0)."
    exit 1
  fi
}

install_all() {
  echo "[INFO] Installing systemd upgrade service + timer ..."

  # Ensure directories exist
  install -d -m 0755 /var/log /usr/local/bin /var/lib/upgrade /run/upgrade
  touch "$LOG_FILE"
  chmod 0644 "$LOG_FILE"

  echo "[INFO] Writing $SCRIPT_PATH ..."
  cat > "$SCRIPT_PATH" <<'EOF'
#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# System Upgrade Automation Script
#
# Description:
#   This script automates daily system upgrades on Debian-based systems.
#   It ensures upgrades are performed only once per day, avoids concurrent runs,
#   handles errors gracefully, and logs detailed upgrade information.
#
# Features:
#   - Strict error handling with set -Eeuo pipefail
#   - Flock-based locking to prevent concurrent runs
#   - Runs only once per day (tracked via timestamp file)
#   - Captures full apt-get output to temporary files
#   - Extracts and logs both summary statistics and package details
#   - Performs dpkg --configure -a before upgrades to recover from interruptions
#   - Runs apt-get full-upgrade with phased updates enabled
#   - Cleans up with apt-get autoremove and apt-get clean
#   - Debug mode via DEBUG=1 environment variable
#   - All operations logged to /var/log/upgrade.log
#
# Behaviour:
#   1. Check if upgrade already ran today (exit if yes)
#   2. Start logging and acquire exclusive lock (exit if another instance is running)
#   3. Recover any interrupted package installations (dpkg --configure -a)
#   4. Update package lists (apt-get update)
#   5. Perform full-upgrade and log summary + package details
#   6. Autoremove obsolete packages and log summary + package details
#   7. Clean package cache (apt-get clean)
#   8. Record successful run timestamp
#
# Log Output Format:
#   [INFO] upgrade summary: <summary>      → Package counts (upgraded, installed, removed)
#   [INFO] upgrade details: <details>      → Actual package names
#   [INFO] autoremove summary: <summary>   → Autoremove package counts
#   [INFO] autoremove details: <details>   → Removed package names
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# License: MIT
# Version: 5.0
# -----------------------------------------------------------------------------

set -Eeuo pipefail
umask 077

# ----------------------------- Configuration ----------------------------------
TIMESTAMP_FILE="/var/lib/upgrade/last_upgrade_check"
LOCK_FILE="/run/upgrade/upgrade.lock"
LOG_FILE="/var/log/upgrade.log"

# Force noninteractive APT to suppress prompts during upgrade
export DEBIAN_FRONTEND=noninteractive

DEBUG="${DEBUG:-0}"

# ----------------------------- Helper Functions -------------------------------
# Extract summary line matching apt-get output pattern
extract_summary() {
  local apt_output_file
  apt_output_file="$1"
  grep -E '^[0-9]+ upgraded, [0-9]+ newly installed, [0-9]+ to remove and [0-9]+ not upgraded' "$apt_output_file" 2>/dev/null || printf 'see full upgrade log'
}

# Extract package details (upgraded/removed) from apt-get output
extract_details() {
  local apt_output_file packages upgraded removed installed
  apt_output_file="$1"
  packages=""

  # Extract upgraded packages (between "The following packages will be upgraded:" and summary line)
  upgraded=$(awk '/^The following packages will be upgraded:$/ {found=1; next}
                   found && /^[0-9]+ upgraded,/ {exit}
                   found && NF {print}' "$apt_output_file" 2>/dev/null \
    | tr '\n' ' ' \
    | tr -cd '[:print:] ' \
    | sed 's/  */ /g' \
    | sed 's/^ //;s/ $//')

  # Extract removed packages (between "The following packages will be REMOVED:" and summary/next section)
  removed=$(awk '/^The following packages will be REMOVED:$/ {found=1; next}
                 found && /^[0-9]+ upgraded,/ {exit}
                 found && /^The following/ {exit}
                 found && NF {print}' "$apt_output_file" 2>/dev/null \
    | tr '\n' ' ' \
    | tr -cd '[:print:] ' \
    | sed 's/  */ /g' \
    | sed 's/^ //;s/ $//')

  # Extract newly installed packages (between "The following NEW packages will be installed:" and summary/next section)
  installed=$(awk '/^The following NEW packages will be installed:$/ {found=1; next}
                   found && /^[0-9]+ upgraded,/ {exit}
                   found && /^The following/ {exit}
                   found && NF {print}' "$apt_output_file" 2>/dev/null \
    | tr '\n' ' ' \
    | tr -cd '[:print:] ' \
    | sed 's/  */ /g' \
    | sed 's/^ //;s/ $//')

  # Build output string
  [[ -n "$upgraded" ]] && packages="${packages}upgraded: ${upgraded}; "
  [[ -n "$installed" ]] && packages="${packages}installed: ${installed}; "
  [[ -n "$removed" ]] && packages="${packages}removed: ${removed}; "

  # Return formatted string or empty indicator
  if [[ -n "$packages" ]]; then
    printf '%s' "${packages%; }"
  else
    printf 'no package changes'
  fi
}

# ----------------------------- Error Handling ---------------------------------
# Log failing command, line number, and exit code
trap 'code=$?; err_cmd="${BASH_COMMAND:-unknown}"; err_line="${LINENO}";
  echo "[ERROR] Upgrade failed at line ${err_line} (exit ${code}): ${err_cmd}" | tee -a "$LOG_FILE" 2>/dev/null || true;
  cleanup;
  exit ${code}' ERR

# Always cleanup lock on exit (success or failure)
cleanup() {
  # Close FD first (releases flock if we hold it)
  exec 9>&- 2>/dev/null || true
  # Then remove file (safe after FD close)
  rm -f "$LOCK_FILE" 2>/dev/null || true
}
trap cleanup EXIT

# --------------------------------- Root Check ---------------------------------
if [[ $EUID -ne 0 ]]; then
  echo "[ERROR] This script must be run as root."
  exit 1
fi

# ----------------------------- Timestamp Check --------------------------------
today="$(date +%F)"
last_run=""

# Read the last run date from the timestamp file, if it exists
if [[ -f "$TIMESTAMP_FILE" ]]; then
  last_run="$(<"$TIMESTAMP_FILE")"
fi

# Exit early if the upgrade has already been performed today
if [[ "$last_run" == "$today" ]]; then
  echo "Upgrade already performed today ($today). Skipping."
  exit 0
fi

# ----------------------------- Directory Setup --------------------------------
# Ensure all required directories and log file exist before proceeding
install -d -m 0755 /var/lib/upgrade /run/upgrade /var/log 2>/dev/null || true
touch "$LOG_FILE" 2>/dev/null || true
chmod 0644 "$LOG_FILE" 2>/dev/null || true

echo "[INFO] Starting upgrade on $today" | tee -a "$LOG_FILE"

# ----------------------------- Locking ----------------------------------------
# Standard flock pattern: open FD → acquire lock → work → FD closes → lock releases
echo "[INFO] Attempting to acquire lock: $LOCK_FILE" | tee -a "$LOG_FILE" 2>/dev/null || true

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "[INFO] Another upgrade is running (lock held). Exiting cleanly." | tee -a "$LOG_FILE" 2>/dev/null || true
  # cleanup before exit through EXIT trap
  exit 0
fi

echo "[INFO] Lock acquired successfully." | tee -a "$LOG_FILE"

# ----------------------------- Upgrade Process --------------------------------
if [[ "$DEBUG" == "1" ]]; then
  set -x
fi

echo "[INFO] Running dpkg --configure -a to recover interrupted packages..." | tee -a "$LOG_FILE"
dpkg --configure -a >/dev/null 2>&1 || true
apt-get install -f -y >/dev/null 2>&1 || true

# Update package lists
echo "[INFO] updating package list"
apt-get update >/dev/null 2>&1

# Now perform the upgrade
upgrade_log="$(mktemp)"
apt-get \
  -o APT::Get::Always-Include-Phased-Updates=true \
  -o Dpkg::Options::="--force-confdef" \
  -o Dpkg::Options::="--force-confold" \
  full-upgrade -y >"$upgrade_log" 2>&1
summary_line=$(extract_summary "$upgrade_log")
echo "[INFO] upgrade summary: ${summary_line}" | tee -a "$LOG_FILE"
details_line=$(extract_details "$upgrade_log")
echo "[INFO] upgrade details: ${details_line}" | tee -a "$LOG_FILE"
rm -f "$upgrade_log"

autoremove_log="$(mktemp)"
apt-get autoremove --purge -y >"$autoremove_log" 2>&1
summary_line=$(extract_summary "$autoremove_log")
echo "[INFO] autoremove summary: ${summary_line}" | tee -a "$LOG_FILE"
details_line=$(extract_details "$autoremove_log")
echo "[INFO] autoremove details: ${details_line}" | tee -a "$LOG_FILE"
rm -f "$autoremove_log"

# Clean local package cache (ignore failures)
apt-get clean || true

if [[ "$DEBUG" == "1" ]]; then
  set +x
fi

# ----------------------------- Finalisation -----------------------------------
# Mark successful run by writing today's date to the timestamp file
printf '%s\n' "$today" > "$TIMESTAMP_FILE"
chmod 0644 "$TIMESTAMP_FILE"

echo "[INFO] Upgrade completed successfully on $today" | tee -a "$LOG_FILE"

# ----------------------------- End of Script ----------------------------------
EOF
  chmod 0755 "$SCRIPT_PATH"

  echo "[INFO] Writing $SERVICE_PATH ..."
  cat > "$SERVICE_PATH" <<'EOF'
[Unit]
Description=Daily System Upgrade (oneshot)
Documentation=man:apt-get(8)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/upgrade.sh
User=root
Group=root
Environment=PATH=/usr/sbin:/usr/bin:/sbin:/bin
SyslogIdentifier=upgrade
Nice=10
IOSchedulingClass=best-effort
IOSchedulingPriority=7
StandardOutput=journal
StandardError=journal
EOF
  chmod 0644 "$SERVICE_PATH"

  echo "[INFO] Writing $TIMER_PATH ..."
  cat > "$TIMER_PATH" <<'EOF'
[Unit]
Description=Run Daily System Upgrade

[Timer]
OnCalendar=*-*-* 08:00:00
RandomizedDelaySec=30m
Persistent=true
Unit=upgrade.service

[Install]
WantedBy=timers.target
EOF
  chmod 0644 "$TIMER_PATH"

  echo "[INFO] Writing $STATUS_PATH ..."
  cat > "$STATUS_PATH" <<'EOF'
#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Upgrade Service Status Check Script
#
# Description:
#   Quick status check for the automated upgrade service and timer.
#   Shows current service state, last run details, and next scheduled run.
#
# Usage:
#   status-jobs                      → Run from anywhere (in PATH)
#   bash /usr/local/bin/status-jobs  → Explicit path
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# -----------------------------------------------------------------------------

echo "=== Upgrade Service Status ==="
systemctl --no-pager status upgrade.service
echo
echo "=== Upgrade Timer Status ==="
systemctl --no-pager status upgrade.timer
EOF
  chmod 0755 "$STATUS_PATH"

  echo "[INFO] Reloading systemd units ..."
  systemctl daemon-reload

  echo "[INFO] Enabling and starting upgrade.timer ..."
  systemctl enable --now upgrade.timer

  echo
  echo "[OK] Installed:"
  echo "  - Script     : $SCRIPT_PATH"
  echo "  - Service    : $SERVICE_PATH"
  echo "  - Timer      : $TIMER_PATH"
  echo "  - Status     : $STATUS_PATH"
  echo "  - Log        : $LOG_FILE"
  echo "  - State      : /var/lib/upgrade/last_upgrade_check"
  echo "  - Lock       : /run/upgrade/upgrade.lock"
  echo
  echo "[INFO] Timer status:"
  systemctl status --no-pager upgrade.timer || true
  echo
  echo "[TIP] Status : status-jobs"
  echo "[TIP] Test   : sudo systemctl start upgrade.service"
  echo "[TIP] Debug  : sudo DEBUG=1 /usr/local/bin/upgrade.sh"
  echo "[TIP] Check  : cat /var/lib/upgrade/last_upgrade_check"
  echo "[TIP] Logs   : tail -f /var/log/upgrade.log"
}

uninstall_all() {
  echo "[INFO] Uninstalling systemd upgrade service + timer ..."
  systemctl disable --now upgrade.timer 2>/dev/null || true
  systemctl stop upgrade.service 2>/dev/null || true

  rm -f "$TIMER_PATH" "$SERVICE_PATH" "$SCRIPT_PATH" "$STATUS_PATH"
  systemctl daemon-reload

  rm -f /var/lib/upgrade/last_upgrade_check
  rm -f /run/upgrade/upgrade.lock

  echo "[OK] Uninstalled all components."
  echo "[NOTE] Log retained at: $LOG_FILE"
}

main() {
  require_root
  if [[ "${1:-}" == "--uninstall" ]]; then
    uninstall_all
  else
    install_all
  fi
}

main "$@"
