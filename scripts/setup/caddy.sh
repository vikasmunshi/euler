#!/usr/bin/env bash
# Caddy Setup Script
# ==================
#
# Installs, updates, or removes the Caddy web server used as the HTTPS front end
# for solver-web (see docs/tls-and-auth.md). Caddy terminates TLS and reverse-proxies
# to the aiohttp server on loopback.
#
# Stock Caddy from the official apt repository is sufficient: certificates are
# issued out-of-band by acme.sh (name.com DNS-01) and loaded by Caddy via a `tls`
# directive, so no DNS-provider plugin is compiled in. (The caddy-dns/namedotcom
# plugin is unmaintained and fails to build against current Caddy, which is why
# issuance is delegated to acme.sh rather than Caddy's own ACME.)
#
# The apt package installs and starts a default `caddy.service` bound to the stock
# /etc/caddy/Caddyfile; this script stops and disables it (systemd only) so it does
# not clash on :80/:443 with our own configuration, then installs our own
# `caddy-euler.service` (runs Caddy as the repo owner against ./Caddyfile). That
# unit is enabled immediately and started once the cert + Caddyfile are in place
# (see docs/tls-and-auth.md for the full flow: acme.sh issues the cert Caddy loads).
#
# The Caddyfile itself carries the deployment's hostname, so it is gitignored and
# generated here at install time from a hostname supplied on the command line
# (`install <hostname>`), via $EULER_TLS_DOMAIN, or at an interactive prompt.
#
# Features:
# - Checks for an existing Caddy installation (idempotent install)
# - Adds Caddy's official apt repo (keyring + sources list) if missing
# - Installs / updates the binary via apt
# - Stops and disables the default apt `caddy.service` (systemd only)
# - Generates the Caddyfile for the requested hostname
# - Generates + installs the relocatable caddy-euler.service unit (repo owner + paths)
# - Uninstalls cleanly (package, apt repo config, and the caddy-euler unit)
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

# Caddy official apt repository (Cloudsmith), per https://caddyserver.com/docs/install
CADDY_GPG_URL="https://dl.cloudsmith.io/public/caddy/stable/gpg.key"
CADDY_REPO_URL="https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt"
CADDY_KEYRING="/usr/share/keyrings/caddy-stable-archive-keyring.gpg"
CADDY_SOURCES_LIST="/etc/apt/sources.list.d/caddy-stable.list"

# Our Caddy instance: the systemd unit (generated + installed here) and the Caddyfile
# it serves, both resolved from this script's location so nothing is hard-coded.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CADDYFILE="${PROJECT_ROOT}/Caddyfile"
EULER_SERVICE_NAME="caddy-euler.service"
EULER_SERVICE_DEST="/etc/systemd/system/${EULER_SERVICE_NAME}"

usage() {
    echo "Usage: $0 [install [hostname]|update|service|uninstall|status]"
    echo
    echo "  install [host]  Install Caddy via apt, generate the Caddyfile for <host>"
    echo "                  (prompted, or via \$EULER_TLS_DOMAIN, if omitted), and"
    echo "                  install the caddy-euler.service unit"
    echo "  update     Upgrade an existing apt install to the latest version"
    echo "  service    (Re)install the caddy-euler.service unit, starting it if ready"
    echo "  uninstall  Remove Caddy, its apt repo config, and the caddy-euler unit"
    echo "  status     Show install state, version, and service state (default)"
}

# Verifies that sudo is available and the current user has sudo privileges.
# Prints an error and returns 1 if sudo is missing or the user is not authorised.
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

# Returns 0 if the `caddy` command is resolvable on PATH, 1 otherwise.
caddy_is_installed() {
    command -v caddy &> /dev/null
}

# Print the installed Caddy version, or "unknown".
caddy_version() {
    caddy version 2>/dev/null || echo "unknown"
}

# Adds Caddy's official apt repository (keyring + sources list) if not already present.
add_caddy_apt_repo() {
    if [ -f "${CADDY_KEYRING}" ] && [ -f "${CADDY_SOURCES_LIST}" ]; then
        echo "Caddy apt repository already configured"
        return 0
    fi
    echo "Configuring Caddy apt repository..."
    sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl gpg
    curl -1sLf "${CADDY_GPG_URL}" | sudo gpg --dearmor -o "${CADDY_KEYRING}"
    curl -1sLf "${CADDY_REPO_URL}" | sudo tee "${CADDY_SOURCES_LIST}" > /dev/null
    sudo apt-get update
}

# Stops and disables the default apt `caddy.service`. The apt package binds it to
# the stock /etc/caddy/Caddyfile, which would clash on :80/:443 with the Caddyfile
# the TLS setup runs. No-op when systemd is not the running init (e.g. a WSL distro
# with systemd off) or the unit does not exist.
disable_default_service() {
    if [ ! -d /run/systemd/system ] || ! command -v systemctl &> /dev/null; then
        echo "systemd not active; skipping default caddy.service disable"
        return 0
    fi
    if ! systemctl list-unit-files caddy.service &> /dev/null; then
        return 0
    fi
    echo "Stopping and disabling the default caddy.service (TLS setup runs its own config)..."
    sudo systemctl disable --now caddy.service 2>/dev/null || true
}

# Writes the Caddyfile for HOSTNAME, overwriting any existing one. Caddy terminates
# TLS with the acme.sh-issued cert (loaded via `tls`, paths relative to the unit's
# WorkingDirectory = repo root) and reverse-proxies to the loopback aiohttp server.
# The Caddyfile is gitignored (it carries the deployment hostname) and regenerated
# here, so keep it in sync with the reference in docs/tls-and-auth.md.
generate_caddyfile() {
    local hostname="$1"
    echo "Writing ${CADDYFILE} for ${hostname}..."
    cat > "${CADDYFILE}" <<EOF
# Caddy configuration for the solver-web HTTPS front end.
#
# GENERATED by scripts/setup/caddy.sh install — edits are overwritten on reinstall.
# Caddy terminates TLS and reverse-proxies to the aiohttp server on loopback.
# The certificate is issued out-of-band by acme.sh (name.com DNS-01) and deployed
# to keys/ — Caddy loads it via the \`tls\` directive and performs no ACME itself.
# Cert paths are relative to Caddy's working directory (the repo root, set by
# caddy-euler.service's WorkingDirectory) so this file is not machine-specific.
# See docs/tls-and-auth.md.
{
	# DNS-01 needs no inbound port, so keep Caddy off :80 (no HTTP->HTTPS redirect).
	auto_https disable_redirects
}

${hostname} {
	tls keys/.server.crt keys/.server.key

	# HSTS: the site is HTTPS-only (DNS-01, no :80), so pin HTTPS for a year including
	# subdomains of this host. (docs/security-assessment.md SEC-05.)
	header Strict-Transport-Security "max-age=31536000; includeSubDomains"

	# Overwrite (not append) X-Forwarded-For with the real transport peer, so a client
	# cannot inject a spoofed left-most hop that the app trusts for rate-limiting.
	# (docs/security-assessment.md SEC-04.)
	reverse_proxy 127.0.0.1:8080 {
		header_up X-Forwarded-For {remote_host}
	}
}
EOF
}

# Resolves the front-end hostname and (re)generates the Caddyfile. Precedence:
# an explicit CLI argument, then $EULER_TLS_DOMAIN (shared with acme.sh), then —
# only if no Caddyfile exists yet — an interactive prompt. If none of these yields
# a hostname but a Caddyfile is already present, it is left untouched, so a repeated
# `install` with no argument is idempotent.
ensure_caddyfile() {
    local hostname="${1:-${EULER_TLS_DOMAIN:-}}"
    if [ -z "${hostname}" ]; then
        if [ -f "${CADDYFILE}" ]; then
            echo "Using existing ${CADDYFILE}"
            return 0
        fi
        read -rp "Enter the hostname for the HTTPS front end (e.g. euler.example.com): " hostname
        if [ -z "${hostname}" ]; then
            echo "Error: a hostname is required to generate the Caddyfile" >&2
            return 1
        fi
    fi
    generate_caddyfile "${hostname}"
}

# Generates and installs the caddy-euler.service unit — nothing hard-coded: User/Group
# are the repo owner (so Caddy can read the acme.sh-deployed key), and the working
# directory, binary, and config path are all derived here, so the unit is correct on
# any checkout, user, or machine. The Caddyfile's cert paths are relative to
# WorkingDirectory, so they relocate too. Enables the unit, and starts it only when the
# Caddyfile validates (which also needs the acme.sh cert). No-op without systemd.
install_euler_service() {
    if [ ! -d /run/systemd/system ] || ! command -v systemctl &> /dev/null; then
        echo "systemd not active; skipping ${EULER_SERVICE_NAME} install"
        return 0
    fi
    if ! caddy_is_installed; then
        echo "Warning: caddy not installed; skipping ${EULER_SERVICE_NAME} install" >&2
        return 0
    fi

    local caddy_bin svc_user svc_group
    caddy_bin="$(command -v caddy)"
    svc_user="$(stat -c '%U' "${PROJECT_ROOT}")"
    svc_group="$(stat -c '%G' "${PROJECT_ROOT}")"

    echo "Installing ${EULER_SERVICE_NAME} (User=${svc_user}, WorkingDirectory=${PROJECT_ROOT})..."
    sudo tee "${EULER_SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=Caddy (solver-web HTTPS front end)
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=${svc_user}
Group=${svc_group}
WorkingDirectory=${PROJECT_ROOT}
ExecStart=${caddy_bin} run --config ${CADDYFILE}
ExecReload=${caddy_bin} reload --config ${CADDYFILE} --force
Restart=on-failure
RestartSec=5s
# Bind :443 without running as root.
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable "${EULER_SERVICE_NAME}" 2>/dev/null || true

    # Validate from the working directory so the Caddyfile's relative cert paths resolve.
    if [ -f "${CADDYFILE}" ] && (cd "${PROJECT_ROOT}" && caddy validate --config "${CADDYFILE}") &> /dev/null; then
        if sudo systemctl restart "${EULER_SERVICE_NAME}"; then
            echo "${EULER_SERVICE_NAME} started"
        else
            echo "Warning: ${EULER_SERVICE_NAME} failed to start;" \
                 "check: systemctl status ${EULER_SERVICE_NAME}" >&2
        fi
    else
        echo "${EULER_SERVICE_NAME} enabled but not started: ${CADDYFILE} missing or invalid."
        echo "  Issue the cert first (scripts/setup/acme.sh issue), then: $0 service"
    fi
}

# Stops, disables, and removes the caddy-euler.service unit. No-op when absent.
remove_euler_service() {
    if [ ! -d /run/systemd/system ] || ! command -v systemctl &> /dev/null; then
        return 0
    fi
    if [ -f "${EULER_SERVICE_DEST}" ]; then
        echo "Removing ${EULER_SERVICE_NAME}..."
        sudo systemctl disable --now "${EULER_SERVICE_NAME}" 2>/dev/null || true
        sudo rm -f "${EULER_SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
}

# Installs Caddy via apt. Takes an optional hostname for the generated Caddyfile.
install_caddy() {
    local hostname="${1:-}"
    check_can_sudo || return 1

    if caddy_is_installed; then
        echo "Caddy already installed: $(caddy_version)"
    else
        add_caddy_apt_repo
        echo "Installing Caddy..."
        sudo apt-get install -y caddy
        echo "Caddy installed: $(caddy_version)"
    fi

    disable_default_service
    ensure_caddyfile "${hostname}" || return 1
    install_euler_service
    echo "Caddy setup completed: $(caddy_version)"
}

# Upgrades an existing apt install to the latest version (installs it if missing).
update_caddy() {
    check_can_sudo || return 1

    if ! caddy_is_installed; then
        echo "Caddy is not installed; installing instead..."
        install_caddy
        return 0
    fi

    echo "Updating Caddy..."
    sudo apt-get update
    sudo apt-get install -y --only-upgrade caddy
    disable_default_service
    echo "Caddy now at: $(caddy_version)"
}

# Removes Caddy and its apt repository configuration.
uninstall_caddy() {
    check_can_sudo || return 1

    if ! caddy_is_installed && [ ! -f "${CADDY_SOURCES_LIST}" ] && [ ! -f "${CADDY_KEYRING}" ] \
        && [ ! -f "${EULER_SERVICE_DEST}" ]; then
        echo "Caddy does not appear to be installed"
        return 0
    fi

    remove_euler_service

    if dpkg-query -W -f='${Status}' caddy 2>/dev/null | grep -q "install ok installed"; then
        echo "Uninstalling Caddy..."
        sudo apt-get --purge remove -y caddy
        sudo apt-get autoremove -y
        echo "Caddy package removed"
    fi

    if [ -f "${CADDY_SOURCES_LIST}" ]; then
        echo "Removing Caddy apt sources list ${CADDY_SOURCES_LIST}"
        sudo rm -f "${CADDY_SOURCES_LIST}"
    fi
    if [ -f "${CADDY_KEYRING}" ]; then
        echo "Removing Caddy apt keyring ${CADDY_KEYRING}"
        sudo rm -f "${CADDY_KEYRING}"
    fi

    echo "Caddy uninstallation completed"
}

# Reports install state, version, and default-service state.
status_caddy() {
    if caddy_is_installed; then
        echo "Caddy: ✓ installed ($(command -v caddy))"
        echo "  version: $(caddy_version)"
    else
        echo "Caddy: ✗ not installed"
    fi
    if command -v systemctl &> /dev/null && [ -d /run/systemd/system ] \
        && systemctl list-unit-files caddy.service &> /dev/null; then
        echo "  default caddy.service: $(systemctl is-active caddy 2>/dev/null)/$(systemctl is-enabled caddy 2>/dev/null)"
        echo "    (the TLS setup runs its own config; this default should be inactive/disabled)"
    fi
    if command -v systemctl &> /dev/null && [ -f "${EULER_SERVICE_DEST}" ]; then
        echo "  ${EULER_SERVICE_NAME}: $(systemctl is-active caddy-euler 2>/dev/null)/$(systemctl is-enabled caddy-euler 2>/dev/null)"
    fi
}

# Main execution — defaults to 'status' if no argument provided.
ACTION="${1:-status}"

case "${ACTION}" in
    install)
        install_caddy "${2:-}"
        ;;
    update)
        update_caddy
        ;;
    service)
        check_can_sudo || exit 1
        install_euler_service
        ;;
    uninstall)
        uninstall_caddy
        ;;
    status)
        status_caddy
        ;;
    -h | --help | help)
        usage
        ;;
    *)
        echo "Unknown action: ${ACTION}"
        usage
        exit 1
        ;;
esac
