#!/usr/bin/env bash
# Egress (forward proxy) Setup Script — Phase 2 of the server redesign
# ====================================================================
#
# Installs / uninstalls / upgrades the Squid forward proxy that is the *only* path
# out to the internet for the shell, AI features, the problem scraper, and `gh`. It
# enforces a **domain allowlist** (default-deny), operationalising the "plaintext must
# never leave the repo" rule at the network layer. Sibling to scripts/setup/frontend.sh
# (the inbound edge); see docs/secure-web-server.md (Phase 2, Design decisions DD-1..DD-3).
#
# Model:
#   - Squid listens on loopback 127.0.0.1:3128 (never network-exposed).
#   - Only the allowlisted domains are reachable (CONNECT to :443 + plain :80);
#     everything else is denied. The allowlist is /etc/euler-proxy/squid.allowlist.
#   - Runs as the dedicated `euler-proxy` user (DD-2), in its own group — NOT in
#     `euler-web`, so it has no access to the app sockets.
#   - Config lives in /etc/euler-proxy (root:euler-proxy). The client-side proxy env
#     is written to /etc/euler/egress.env for the app-service units to load
#     (EnvironmentFile=), wiring HTTPS_PROXY for AI/scraper/gh.
#
#   /etc/euler-proxy/squid.conf         root:euler-proxy 0640  (generated here)
#   /etc/euler-proxy/squid.allowlist    root:euler-proxy 0640  (generated if absent; edit + reload)
#   /etc/euler/egress.env               root:root 0644         (HTTPS_PROXY for clients)
#   /etc/systemd/system/euler-proxy.service   (root-owned, boot-enabled)
#
# Because the unit lives in root's systemd and runs as a locked-down user, lifecycle
# (start/stop/restart) requires sudo (DD-3).
#
# Actions: install | uninstall | upgrade | status | reload | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

# ── System locations ──────────────────────────────────────────────────────────────
SYS_DIR="/etc/euler"                       # shared with frontend.sh (egress.env lives here)
PROXY_CONF_DIR="/etc/euler-proxy"          # euler-proxy's own config dir
SQUID_CONF="${PROXY_CONF_DIR}/squid.conf"
ALLOWLIST="${PROXY_CONF_DIR}/squid.allowlist"
EGRESS_ENV="${SYS_DIR}/egress.env"

# ── Service identity (DD-2): euler-proxy is its own user/group, outside euler-web ──
PROXY_USER="euler-proxy"
PROXY_GROUP="euler-proxy"
SERVICE_NAME="euler-proxy.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"

# ── Proxy listener (loopback only) ────────────────────────────────────────────────
PROXY_ADDR="127.0.0.1"
PROXY_PORT="3128"

# ── Default allowlist (leading dot = domain + subdomains). Edit ${ALLOWLIST} to change. ──
DEFAULT_ALLOWLIST=(
    "api.anthropic.com"          # Claude API (AI features)
    ".projecteuler.net"          # problem scraper
    ".github.com"                # gh: repo, API, codeload
    ".githubusercontent.com"     # gh: raw / release objects
)

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|upgrade|status|reload|help]

  install    Install Squid, create the euler-proxy user, generate the allowlist config
             + egress.env, and install the root-owned ${SERVICE_NAME} (boot-enabled).
  uninstall  Remove the unit and Squid; prompt before deleting ${PROXY_CONF_DIR},
             ${EGRESS_ENV}, and the euler-proxy user.
  upgrade    Upgrade Squid and regenerate the config + unit.
  status     Show install state, unit state, and an allow/deny probe through the proxy.
  reload     Reconfigure the running proxy (sudo systemctl reload).

  Listener: ${PROXY_ADDR}:${PROXY_PORT} (loopback). Allowlist: ${ALLOWLIST}.
USAGE
}

# ── Helpers ───────────────────────────────────────────────────────────────────────

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

require_systemd() {
    if [ ! -d /run/systemd/system ] || ! command -v systemctl &> /dev/null; then
        echo "Error: systemd is required for the egress proxy (root-owned unit); not active here." >&2
        return 1
    fi
}

squid_bin() { command -v squid || echo /usr/sbin/squid; }
squid_is_installed() { [ -x "$(command -v squid || echo /usr/sbin/squid)" ]; }
squid_version() { "$(squid_bin)" -v 2>/dev/null | head -n1 || echo "unknown"; }

# ── Squid (apt) ───────────────────────────────────────────────────────────────────

install_squid_pkg() {
    if squid_is_installed; then
        echo "Squid already installed: $(squid_version)"
    else
        echo "Installing Squid..."
        sudo apt-get install -y squid
        echo "Squid installed: $(squid_version)"
    fi
    # The apt package starts a default squid.service on :3128 as the `proxy` user;
    # disable it so it cannot clash with our euler-proxy.service.
    if systemctl list-unit-files squid.service &> /dev/null; then
        echo "Disabling the default squid.service (superseded by ${SERVICE_NAME})..."
        sudo systemctl disable --now squid.service 2>/dev/null || true
    fi
}

# ── Service identity + config (DD-2) ──────────────────────────────────────────────

ensure_proxy_user() {
    if ! getent group "${PROXY_GROUP}" > /dev/null; then
        echo "Creating group ${PROXY_GROUP}..."
        sudo groupadd --system "${PROXY_GROUP}"
    fi
    if ! getent passwd "${PROXY_USER}" > /dev/null; then
        echo "Creating system user ${PROXY_USER} (group ${PROXY_GROUP})..."
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
            -g "${PROXY_GROUP}" "${PROXY_USER}"
    fi
}

ensure_dirs() {
    sudo install -d -o root -g "${PROXY_GROUP}" -m 0750 "${PROXY_CONF_DIR}"
    sudo mkdir -p "${SYS_DIR}"          # shared dir; frontend.sh owns its perms if present
}

# Write the default allowlist only if absent, so operator edits survive `upgrade`.
generate_allowlist() {
    if sudo test -f "${ALLOWLIST}"; then
        echo "Keeping existing allowlist ${ALLOWLIST}"
        return 0
    fi
    echo "Writing default allowlist ${ALLOWLIST}..."
    printf '%s\n' "${DEFAULT_ALLOWLIST[@]}" | sudo tee "${ALLOWLIST}" > /dev/null
    sudo chown root:"${PROXY_GROUP}" "${ALLOWLIST}"
    sudo chmod 0640 "${ALLOWLIST}"
}

generate_squid_conf() {
    echo "Writing ${SQUID_CONF}..."
    sudo tee "${SQUID_CONF}" > /dev/null <<EOF
# Squid forward proxy for euler egress (Phase 2).
#
# GENERATED by scripts/setup/egress.sh — edits are overwritten on install/upgrade
# (edit the allowlist at ${ALLOWLIST} instead). Default-deny domain allowlist; loopback
# only. See docs/secure-web-server.md.

http_port ${PROXY_ADDR}:${PROXY_PORT}
visible_hostname euler-proxy

acl SSL_ports port 443
acl Safe_ports port 80
acl Safe_ports port 443
acl CONNECT method CONNECT

# The allowlist: one domain per line; a leading dot also matches subdomains.
acl allowed_domains dstdomain "${ALLOWLIST}"

# Default-deny: refuse unsafe ports and any CONNECT to a non-TLS port, then permit
# only the allowlisted domains and deny everything else.
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow allowed_domains
http_access deny all

# Pure gateway: no disk cache, and do not leak client/proxy identity upstream.
cache deny all
via off
forwarded_for delete
httpd_suppress_version_string on

# Runtime paths (systemd provides these dirs, owned by ${PROXY_USER}).
pid_filename /run/euler-proxy/squid.pid
access_log stdio:/var/log/euler-proxy/access.log
cache_log /var/log/euler-proxy/cache.log
coredump_dir /var/cache/euler-proxy
shutdown_lifetime 5 seconds
EOF
    sudo chown root:"${PROXY_GROUP}" "${SQUID_CONF}"
    sudo chmod 0640 "${SQUID_CONF}"
}

# The client-side proxy env the app-service units load (EnvironmentFile=) so AI
# features, the scraper, and gh egress only via Squid. Not secret -> world-readable.
generate_egress_env() {
    echo "Writing ${EGRESS_ENV}..."
    sudo tee "${EGRESS_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/egress.sh. Route outbound HTTP(S) through the euler
# egress proxy (Squid allowlist). Loaded by app-service units via EnvironmentFile=;
# see docs/secure-web-server.md (Phase 2). To use it in a shell:  set -a; . ${EGRESS_ENV}
HTTP_PROXY=http://${PROXY_ADDR}:${PROXY_PORT}
HTTPS_PROXY=http://${PROXY_ADDR}:${PROXY_PORT}
http_proxy=http://${PROXY_ADDR}:${PROXY_PORT}
https_proxy=http://${PROXY_ADDR}:${PROXY_PORT}
NO_PROXY=localhost,127.0.0.1,::1
no_proxy=localhost,127.0.0.1,::1
EOF
    sudo chown root:root "${EGRESS_ENV}"
    sudo chmod 0644 "${EGRESS_ENV}"
}

# ── systemd unit (root-owned, boot-enabled; DD-3) ─────────────────────────────────

install_service() {
    require_systemd || return 1
    if ! squid_is_installed; then
        echo "Warning: squid not installed; skipping ${SERVICE_NAME}" >&2
        return 0
    fi
    local squid
    squid="$(squid_bin)"

    echo "Installing ${SERVICE_NAME} (User=${PROXY_USER})..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler egress proxy (Squid, domain allowlist)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/secure-web-server.md
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${PROXY_USER}
Group=${PROXY_GROUP}
ExecStart=${squid} -N -f ${SQUID_CONF}
ExecReload=${squid} -k reconfigure -f ${SQUID_CONF}
Restart=on-failure
RestartSec=5s

# Writable runtime / logs / spool, owned by ${PROXY_USER}.
RuntimeDirectory=euler-proxy
LogsDirectory=euler-proxy
CacheDirectory=euler-proxy

# Hardening (loopback listener on :3128 needs no privileged port).
NoNewPrivileges=true
ProtectHome=true
ProtectSystem=full
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}" 2>/dev/null || true

    if sudo "${squid}" -k parse -f "${SQUID_CONF}" &> /dev/null; then
        if sudo systemctl restart "${SERVICE_NAME}"; then
            echo "${SERVICE_NAME} started"
        else
            echo "Warning: ${SERVICE_NAME} failed to start; check: systemctl status ${SERVICE_NAME}" >&2
        fi
    else
        echo "${SERVICE_NAME} enabled but not started: ${SQUID_CONF} did not parse."
    fi
}

remove_service() {
    if [ -f "${SERVICE_DEST}" ]; then
        echo "Removing ${SERVICE_NAME}..."
        sudo systemctl disable --now "${SERVICE_NAME}" 2>/dev/null || true
        sudo rm -f "${SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
}

# ── Probe: a CONNECT through the proxy succeeds for an allowlisted domain and is
#    refused for anything else. Returns the HTTP code (000 = blocked/unreachable).
#    curl's -w already prints 000 on failure; capture it (|| true so set -e is happy)
#    rather than appending another 000.
_probe() {
    local code
    code="$(curl -sS -o /dev/null -w '%{http_code}' -x "http://${PROXY_ADDR}:${PROXY_PORT}" \
        --max-time 12 "$1" 2>/dev/null || true)"
    printf '%s' "${code:-000}"
}

# ── Allow-probe with a short settle retry: right after `install`, Squid may not
#    yet be ready to dial upstream and refuses the first CONNECT, printing a false
#    ✗ HTTP 000. Retry the *allow* probe until it succeeds (a warm proxy passes on
#    the first try, so this adds no delay to the common path).
_probe_allow() {
    local code i
    for i in 1 2 3 4 5; do
        code="$(_probe "$1")"
        [[ "${code}" =~ ^[23] ]] && { printf '%s' "${code}"; return; }
        sleep 1
    done
    printf '%s' "${code:-000}"
}

# ── Actions ───────────────────────────────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1

    install_squid_pkg
    ensure_proxy_user
    ensure_dirs
    generate_allowlist
    generate_squid_conf
    generate_egress_env
    install_service
    echo "Egress proxy setup complete (${PROXY_ADDR}:${PROXY_PORT})."
    do_status || true
}

do_upgrade() {
    check_can_sudo || return 1
    require_systemd || return 1

    if squid_is_installed; then
        echo "Upgrading Squid..."
        sudo apt-get update
        sudo apt-get install -y --only-upgrade squid
    else
        install_squid_pkg
    fi
    ensure_proxy_user
    ensure_dirs
    generate_allowlist          # keeps existing edits
    generate_squid_conf
    generate_egress_env
    install_service
    echo "Egress upgrade complete: $(squid_version)"
}

do_reload() {
    check_can_sudo || return 1
    sudo systemctl reload "${SERVICE_NAME}"
    echo "Reloaded ${SERVICE_NAME}"
}

do_uninstall() {
    check_can_sudo || return 1
    remove_service

    if dpkg-query -W -f='${Status}' squid 2>/dev/null | grep -q "install ok installed"; then
        echo "Uninstalling Squid..."
        sudo apt-get --purge remove -y squid
        sudo apt-get autoremove -y
    fi

    local reply
    read -r -p "Remove ${PROXY_CONF_DIR} and ${EGRESS_ENV}? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        sudo rm -rf "${PROXY_CONF_DIR}"
        sudo rm -f "${EGRESS_ENV}"
    fi

    read -r -p "Remove service user ${PROXY_USER} and group ${PROXY_GROUP}? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        if getent passwd "${PROXY_USER}" > /dev/null; then sudo userdel "${PROXY_USER}" 2>/dev/null || true; fi
        if getent group "${PROXY_GROUP}" > /dev/null; then sudo groupdel "${PROXY_GROUP}" 2>/dev/null || true; fi
    fi
    echo "Egress uninstall complete."
}

do_status() {
    if squid_is_installed; then
        echo "Squid:      ✓ installed ($(squid_bin)) — $(squid_version)"
    else
        echo "Squid:      ✗ not installed"
    fi
    if command -v systemctl &> /dev/null && [ -f "${SERVICE_DEST}" ]; then
        echo "${SERVICE_NAME}: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null)/$(systemctl is-enabled "${SERVICE_NAME}" 2>/dev/null)"
    else
        echo "${SERVICE_NAME}: ✗ not installed"
    fi
    if sudo test -f "${ALLOWLIST}"; then
        echo "Allowlist (${ALLOWLIST}):"
        sudo grep -vE '^\s*(#|$)' "${ALLOWLIST}" | sed 's/^/  /'
    fi
    # Allow/deny probe through the proxy.
    local allow deny
    allow="$(_probe_allow https://projecteuler.net/)"
    deny="$(_probe https://example.com/)"
    if [[ "${allow}" =~ ^[23] ]]; then
        echo "allow probe (projecteuler.net): ✓ HTTP ${allow}"
    else
        echo "allow probe (projecteuler.net): ✗ HTTP ${allow} (expected 2xx/3xx)"
    fi
    if [ "${deny}" = "000" ] || [ "${deny}" = "403" ]; then
        echo "deny probe  (example.com):      ✓ blocked (HTTP ${deny})"
    else
        echo "deny probe  (example.com):      ✗ NOT blocked (HTTP ${deny})"
    fi
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install ;;
    uninstall) do_uninstall ;;
    upgrade)   do_upgrade ;;
    reload)    do_reload ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac
