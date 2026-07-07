#!/usr/bin/env bash
# Frontend (web edge) Setup Script — Phase 1 of the server redesign
# =================================================================
#
# Single orchestrator for the solver web edge: installs / uninstalls / upgrades
# Caddy (TLS + reverse-proxy edge) and the acme.sh cert client, creates the
# dedicated service identities, generates the Caddyfile router, and installs the
# root-owned systemd unit. Supersedes the old scripts/setup/caddy.sh +
# scripts/setup/acme.sh. See docs/server-redesign.md (Design decisions DD-1..DD-3).
#
# Phase-1 topology:
#   - Caddy terminates TLS on :443 and, for now, serves only a Caddy-native health
#     endpoint (`/healthz` -> 200) plus a maintenance placeholder. App-service
#     upstreams (unix sockets under /run/euler) and the forward_auth gate are added
#     by later phases; the Caddyfile ships them as commented stubs.
#   - The cert is issued out-of-band by acme.sh via DNS-01 (Caddy performs no ACME).
#
# Service identity (DD-2):
#   - group  `euler-web` — the shared group whose members may reach the app sockets.
#   - user   `euler-caddy` — runs the edge; member of `euler-web`; binds :443 via
#     CAP_NET_BIND_SERVICE. (euler-auth / euler-content / euler-ws / euler-proxy are
#     created by their own phases.)
#
# Config + secrets live under /etc/euler, NOT in the repo: the dedicated `euler-caddy`
# user cannot traverse the repo owner's 0750 home dir, so the edge is fully decoupled
# from the checkout (DD, discovered in Phase 1). acme.sh therefore runs as **root**
# (installed under /root/.acme.sh) so its renewal cron can rewrite /etc/euler/tls and
# reload the unit without a sudo prompt.
#
#   /etc/euler/Caddyfile          root:euler-web 0640   (generated here)
#   /etc/euler/tls/server.crt     root:euler-web 0644
#   /etc/euler/tls/server.key     root:euler-web 0640   (readable by euler-caddy)
#   /etc/systemd/system/euler-caddy.service   (root-owned, boot-enabled)
#
# The Caddyfile carries the deployment hostname, so it is host-specific and generated
# here at install time from a hostname on the command line (`install <hostname>`), via
# $EULER_TLS_DOMAIN, or an interactive prompt.
#
# Because the unit lives in root's systemd and runs as a locked-down user, lifecycle
# (start/stop/restart) requires sudo (DD-3).
#
# Actions: install [host] | uninstall | upgrade | status | renew | reload | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

# ── Paths, derived from this script's location so nothing is machine-specific ──────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ── System locations (edge is decoupled from the repo — see header) ───────────────
SYS_DIR="/etc/euler"
CADDYFILE="${SYS_DIR}/Caddyfile"
TLS_DIR="${SYS_DIR}/tls"
CERT_FILE="${TLS_DIR}/server.crt"          # full chain
KEY_FILE="${TLS_DIR}/server.key"           # private key (readable by euler-web)

# ── Service identity (DD-2) ───────────────────────────────────────────────────────
WEB_GROUP="euler-web"
CADDY_USER="euler-caddy"
SERVICE_NAME="euler-caddy.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"

# ── Caddy apt repository (Cloudsmith), per https://caddyserver.com/docs/install ───
CADDY_GPG_URL="https://dl.cloudsmith.io/public/caddy/stable/gpg.key"
CADDY_REPO_URL="https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt"
CADDY_KEYRING="/usr/share/keyrings/caddy-stable-archive-keyring.gpg"
CADDY_SOURCES_LIST="/etc/apt/sources.list.d/caddy-stable.list"

# ── acme.sh, installed and run as root so renewals are unattended ─────────────────
ACME_HOME="/root/.acme.sh"
ACME_BIN="${ACME_HOME}/acme.sh"
ACME_INSTALL_URL="https://get.acme.sh"

# ── Overridable via environment (also via CLI arg for the domain) ─────────────────
DOMAIN="${EULER_TLS_DOMAIN:-euler.vikasmunshi.com}"
ACME_EMAIL="${EULER_TLS_EMAIL:-vikas.munshi@gmail.com}"
DNS_PROVIDER="${EULER_TLS_DNS_PROVIDER:-namecom}"
ENV_FILE="${PROJECT_ROOT}/keys/.env"       # DNS provider credentials (read as the caller)

# acme.sh re-runs this on every renewal: it re-applies the euler-web ownership/mode
# that --install-cert resets to root:root, then reloads the edge (best effort — on
# first issue the unit may not be up yet).
RELOAD_CMD="chown root:${WEB_GROUP} ${CERT_FILE} ${KEY_FILE}; chmod 0644 ${CERT_FILE}; chmod 0640 ${KEY_FILE}; systemctl reload ${SERVICE_NAME} 2>/dev/null || true"

usage() {
    cat <<USAGE
Usage: $0 [install [hostname]|uninstall|upgrade|status|renew|reload|help]

  install [host]  Full edge setup: create euler-web group + euler-caddy user,
                  install Caddy + acme.sh, generate /etc/euler/Caddyfile for <host>
                  (prompted / \$EULER_TLS_DOMAIN if omitted), issue+deploy the cert,
                  and install the root-owned ${SERVICE_NAME} (boot-enabled).
  uninstall       Remove the unit and Caddy; prompt before deleting /etc/euler,
                  acme.sh, and the service users/group.
  upgrade         Upgrade Caddy + acme.sh and regenerate the Caddyfile + unit.
  status          Show install state, cert expiry, unit state, and a /healthz ping.
  renew           Force-renew the certificate now (as root; creds cached by acme.sh).
  reload          Reload the running edge (sudo systemctl reload).

  DNS provider (\$EULER_TLS_DNS_PROVIDER, default ${DNS_PROVIDER}): one of
  namecom, cloudflare, route53, godaddy, digitalocean, gandi.
USAGE
}

# ── Helpers ───────────────────────────────────────────────────────────────────────

# Verify sudo is available and the caller has privileges; else fail early.
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
        echo "Error: systemd is required for the edge (root-owned units); it is not active here." >&2
        return 1
    fi
}

caddy_is_installed() { command -v caddy &> /dev/null; }
caddy_version() { caddy version 2>/dev/null | head -n1 || echo "unknown"; }
caddy_bin() { command -v caddy; }

# ── Caddy (apt) ───────────────────────────────────────────────────────────────────

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

# Stop and disable any Caddy unit that would clash on :80/:443 with our own — the
# stock apt `caddy.service`, and the old repo-owner `caddy-euler.service` this script
# replaces. No-op when absent.
disable_conflicting_services() {
    local unit
    for unit in caddy.service caddy-euler.service; do
        if systemctl list-unit-files "${unit}" &> /dev/null; then
            echo "Disabling ${unit} (superseded by ${SERVICE_NAME})..."
            sudo systemctl disable --now "${unit}" 2>/dev/null || true
        fi
    done
    if [ -f "/etc/systemd/system/caddy-euler.service" ]; then
        sudo rm -f "/etc/systemd/system/caddy-euler.service"
        sudo systemctl daemon-reload
    fi
}

install_caddy_pkg() {
    if caddy_is_installed; then
        echo "Caddy already installed: $(caddy_version)"
    else
        add_caddy_apt_repo
        echo "Installing Caddy..."
        sudo apt-get install -y caddy
        echo "Caddy installed: $(caddy_version)"
    fi
    disable_conflicting_services
}

# ── Service identity + system dirs (DD-2) ─────────────────────────────────────────

ensure_group_and_users() {
    if ! getent group "${WEB_GROUP}" > /dev/null; then
        echo "Creating group ${WEB_GROUP}..."
        sudo groupadd --system "${WEB_GROUP}"
    fi
    # Phase 1 creates only the edge user; euler-auth / euler-content / euler-ws /
    # euler-proxy are created by their own phases.
    if ! getent passwd "${CADDY_USER}" > /dev/null; then
        echo "Creating system user ${CADDY_USER} (group ${WEB_GROUP})..."
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
            -g "${WEB_GROUP}" "${CADDY_USER}"
    else
        sudo usermod -g "${WEB_GROUP}" "${CADDY_USER}" || true
    fi
}

ensure_sys_dirs() {
    sudo install -d -o root -g "${WEB_GROUP}" -m 0750 "${SYS_DIR}"
    sudo install -d -o root -g "${WEB_GROUP}" -m 0750 "${TLS_DIR}"
}

# ── acme.sh (as root) ─────────────────────────────────────────────────────────────

acme_is_installed() { sudo test -x "${ACME_BIN}"; }

# Run acme.sh as clean root. acme.sh refuses to run under `sudo` (it detects the
# SUDO_* env vars and points at its sudo wiki), so strip those markers and pin HOME to
# /root (its working dir is /root/.acme.sh). For calls needing extra environment (the
# DNS credentials at issue time) use `acme_env` to prepend `VAR=val` pairs.
ACME_CLEAN_ENV=(env -u SUDO_COMMAND -u SUDO_USER -u SUDO_UID -u SUDO_GID HOME=/root)
acme_root() {
    sudo "${ACME_CLEAN_ENV[@]}" "${ACME_BIN}" "$@"
}
# Like acme_root, but injects the DNS-credential env pairs collected in $cred_env
# *before* the acme.sh binary so acme.sh sees them as environment, not arguments.
acme_root_with_creds() {
    sudo "${ACME_CLEAN_ENV[@]}" "${cred_env[@]}" "${ACME_BIN}" "$@"
}

install_acme() {
    if ! command -v curl &> /dev/null; then
        echo "Error: curl is required to install acme.sh" >&2
        return 1
    fi
    if acme_is_installed; then
        echo "acme.sh already installed (root): $(acme_root --version 2>/dev/null | tail -n1)"
    else
        echo "Installing acme.sh as root (into ${ACME_HOME})..."
        sudo env HOME=/root sh -c "curl -fsSL '${ACME_INSTALL_URL}' | sh -s email='${ACME_EMAIL}'"
    fi
    acme_root --set-default-ca --server letsencrypt
    echo "acme.sh ready (default CA: Let's Encrypt)"
}

# Resolve $DNS_PROVIDER to its acme.sh hook (into $DNS_HOOK) and the required credential
# variable names (into the $REQUIRED array), loading values from keys/.env (read as the
# caller) or the environment. Errors on an unknown provider or missing credentials.
DNS_HOOK=""
REQUIRED=()
load_dns_creds() {
    if [ -f "${ENV_FILE}" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${ENV_FILE}"
        set +a
    fi
    case "${DNS_PROVIDER}" in
        namecom)
            DNS_HOOK="dns_namecom"
            : "${Namecom_Username:=${NAMEDOTCOM_USERNAME:-}}"
            : "${Namecom_Token:=${NAMEDOTCOM_TOKEN:-}}"
            REQUIRED=(Namecom_Username Namecom_Token) ;;
        cloudflare | cf)
            DNS_HOOK="dns_cf"; REQUIRED=(CF_Token CF_Account_ID) ;;
        route53 | aws)
            DNS_HOOK="dns_aws"; REQUIRED=(AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY) ;;
        godaddy | gd)
            DNS_HOOK="dns_gd"; REQUIRED=(GD_Key GD_Secret) ;;
        digitalocean | do)
            DNS_HOOK="dns_dgon"; REQUIRED=(DO_API_KEY) ;;
        gandi)
            DNS_HOOK="dns_gandi_livedns"; REQUIRED=(GANDI_LIVEDNS_KEY) ;;
        *)
            echo "Error: unsupported DNS provider '${DNS_PROVIDER}'." >&2
            echo "Supported: namecom, cloudflare, route53, godaddy, digitalocean, gandi" >&2
            return 1 ;;
    esac
    local missing=() var
    for var in "${REQUIRED[@]}"; do
        [ -z "${!var:-}" ] && missing+=("${var}")
    done
    if [ "${#missing[@]}" -ne 0 ]; then
        echo "Error: missing ${DNS_PROVIDER} credentials: ${missing[*]}" >&2
        echo "Add them to ${ENV_FILE} (or export them)." >&2
        return 1
    fi
}

# Issue (DNS-01) + deploy the cert into /etc/euler/tls as root, registering the
# perms-fixing reload command. acme.sh caches the DNS creds for future renewals, so
# they are only supplied here at issue time.
issue_cert() {
    load_dns_creds || return 1
    local -a cred_env=() var
    for var in "${REQUIRED[@]}"; do cred_env+=("${var}=${!var}"); done

    echo "Issuing certificate for ${DOMAIN} via ${DNS_PROVIDER} DNS-01 (${DNS_HOOK})..."
    local rc=0
    acme_root_with_creds --issue --dns "${DNS_HOOK}" -d "${DOMAIN}" || rc=$?
    # exit code 2 = "skipped, still valid" — success for our purposes.
    if [ "${rc}" -ne 0 ] && [ "${rc}" -ne 2 ]; then
        echo "Error: certificate issuance failed (acme.sh exit ${rc})" >&2
        return "${rc}"
    fi

    echo "Deploying certificate to ${TLS_DIR}..."
    acme_root --install-cert -d "${DOMAIN}" \
        --fullchain-file "${CERT_FILE}" \
        --key-file "${KEY_FILE}" \
        --reloadcmd "${RELOAD_CMD}"
    if ! sudo test -f "${CERT_FILE}" || ! sudo test -f "${KEY_FILE}"; then
        echo "Error: cert/key were not installed" >&2
        return 1
    fi
    # Apply the euler-web ownership/mode now (the reloadcmd re-applies on every renewal).
    sudo chown root:"${WEB_GROUP}" "${CERT_FILE}" "${KEY_FILE}"
    sudo chmod 0644 "${CERT_FILE}"
    sudo chmod 0640 "${KEY_FILE}"
    echo "Deployed cert -> ${CERT_FILE} (root:${WEB_GROUP} 0644)"
    echo "Deployed key  -> ${KEY_FILE} (root:${WEB_GROUP} 0640)"
}

# ── Caddyfile router (Phase 1) ────────────────────────────────────────────────────

# Resolve the hostname (CLI arg, then $EULER_TLS_DOMAIN, then existing Caddyfile, then
# prompt) into $DOMAIN and (re)generate /etc/euler/Caddyfile.
ensure_caddyfile() {
    local hostname="${1:-${EULER_TLS_DOMAIN:-}}"
    # No hostname given: reuse the one baked into an existing Caddyfile (so re-run and
    # `upgrade` keep the host and pick up template changes), else prompt.
    if [ -z "${hostname}" ] && sudo test -f "${CADDYFILE}"; then
        hostname="$(sudo grep -m1 -oE '^[A-Za-z0-9.-]+ \{' "${CADDYFILE}" | awk '{print $1}')"
    fi
    if [ -z "${hostname}" ]; then
        read -rp "Enter the hostname for the HTTPS front end (e.g. euler.example.com): " hostname
        if [ -z "${hostname}" ]; then
            echo "Error: a hostname is required to generate the Caddyfile" >&2
            return 1
        fi
    fi
    DOMAIN="${hostname}"
    generate_caddyfile
}

generate_caddyfile() {
    echo "Writing ${CADDYFILE} for ${DOMAIN}..."
    sudo tee "${CADDYFILE}" > /dev/null <<EOF
# Caddy configuration for the solver web edge (Phase 1).
#
# GENERATED by scripts/setup/frontend.sh — edits are overwritten on install/upgrade.
# Caddy terminates TLS and, for now, serves only a health endpoint + a maintenance
# placeholder. App-service upstreams (unix sockets under /run/euler) and the
# forward_auth gate are added by later phases (see the commented stubs below and
# docs/server-redesign.md). The cert is issued out-of-band by acme.sh (DNS-01) into
# ${TLS_DIR}; Caddy loads it via \`tls\` and performs no ACME itself.
{
	# DNS-01 needs no inbound :80, so keep Caddy off :80 (no HTTP->HTTPS redirect).
	auto_https disable_redirects
}

${DOMAIN} {
	tls ${CERT_FILE} ${KEY_FILE}

	# Transport-level security headers. The per-response nonce'd CSP is minted by the
	# app tier in later phases; this is the static/edge fallback. (docs/server-redesign.md,
	# docs/security-assessment.md SEC-04/SEC-05.)
	header {
		Strict-Transport-Security "max-age=31536000; includeSubDomains"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "no-referrer"
		Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
		-Server
	}

	# Health probe — Caddy-native, no upstream (Phase 1).
	handle /healthz {
		respond "ok" 200
	}

	# --- Later phases: app services over unix sockets under /run/euler ---
	# Phase 4 forward_auth gates everything except /healthz:
	#   forward_auth unix//run/euler/auth.sock {
	#       uri /verify
	#       copy_headers X-User
	#   }
	# Phase 6 shell WebSocket:
	#   handle_path /ws* { reverse_proxy unix//run/euler/ws.sock }
	# Phase 5 content:
	#   handle          { reverse_proxy unix//run/euler/content.sock }

	# Until app services exist, everything else is the maintenance holding page (Phase 3).
	handle {
		respond "euler - under maintenance" 200
	}
}
EOF
    sudo chown root:"${WEB_GROUP}" "${CADDYFILE}"
    sudo chmod 0640 "${CADDYFILE}"
}

# Validate the Caddyfile (as root, so it can read the 0640 file and 0640 key).
validate_caddyfile() {
    sudo "$(caddy_bin)" validate --config "${CADDYFILE}" &> /dev/null
}

# ── systemd unit (root-owned, boot-enabled; DD-3) ─────────────────────────────────

install_service() {
    require_systemd || return 1
    if ! caddy_is_installed; then
        echo "Warning: caddy not installed; skipping ${SERVICE_NAME}" >&2
        return 0
    fi
    local caddy
    caddy="$(caddy_bin)"

    echo "Installing ${SERVICE_NAME} (User=${CADDY_USER}, Group=${WEB_GROUP})..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler web edge (Caddy)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/server-redesign.md
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=${CADDY_USER}
Group=${WEB_GROUP}
ExecStart=${caddy} run --config ${CADDYFILE}
ExecReload=${caddy} reload --config ${CADDYFILE} --force
Restart=on-failure
RestartSec=5s
WorkingDirectory=${SYS_DIR}

# Bind :443 as a non-root user.
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE

# Writable runtime (future /run/euler sockets) + state (euler-caddy has no home).
RuntimeDirectory=euler
RuntimeDirectoryMode=0770
RuntimeDirectoryPreserve=yes
StateDirectory=euler-caddy
Environment=XDG_DATA_HOME=/var/lib/euler-caddy
Environment=XDG_CONFIG_HOME=/var/lib/euler-caddy

# Hardening.
NoNewPrivileges=true
ProtectHome=true
ProtectSystem=full
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}" 2>/dev/null || true

    if sudo test -f "${CADDYFILE}" && sudo test -f "${CERT_FILE}" && validate_caddyfile; then
        if sudo systemctl restart "${SERVICE_NAME}"; then
            echo "${SERVICE_NAME} started"
        else
            echo "Warning: ${SERVICE_NAME} failed to start; check: systemctl status ${SERVICE_NAME}" >&2
        fi
    else
        echo "${SERVICE_NAME} enabled but not started: Caddyfile/cert missing or invalid."
        echo "  Fix the cert, then: $0 status / sudo systemctl start ${SERVICE_NAME}"
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

# ── Actions ───────────────────────────────────────────────────────────────────────

do_install() {
    local hostname="${1:-}"
    check_can_sudo || return 1
    require_systemd || return 1

    install_caddy_pkg
    ensure_group_and_users
    ensure_sys_dirs
    ensure_caddyfile "${hostname}" || return 1
    install_acme
    issue_cert
    install_service
    echo "Frontend edge setup complete for ${DOMAIN}."
    do_status || true
}

do_upgrade() {
    check_can_sudo || return 1
    require_systemd || return 1

    if caddy_is_installed; then
        echo "Upgrading Caddy..."
        sudo apt-get update
        sudo apt-get install -y --only-upgrade caddy
    else
        echo "Caddy not installed; installing..."
        install_caddy_pkg
    fi
    disable_conflicting_services
    if acme_is_installed; then
        echo "Upgrading acme.sh..."
        acme_root --upgrade || true
    fi
    ensure_group_and_users
    ensure_sys_dirs
    ensure_caddyfile "" || return 1   # regenerate from the existing hostname
    install_service                    # re-lay the unit and reload
    echo "Frontend upgrade complete: $(caddy_version)"
}

do_renew() {
    check_can_sudo || return 1
    if ! acme_is_installed; then
        echo "Error: acme.sh is not installed (root); run '$0 install' first." >&2
        return 1
    fi
    echo "Renewing certificate for ${DOMAIN} (force)..."
    acme_root --renew -d "${DOMAIN}" --force
    echo "Renewal complete for ${DOMAIN}"
}

do_reload() {
    check_can_sudo || return 1
    sudo systemctl reload "${SERVICE_NAME}"
    echo "Reloaded ${SERVICE_NAME}"
}

do_uninstall() {
    check_can_sudo || return 1
    remove_service

    if dpkg-query -W -f='${Status}' caddy 2>/dev/null | grep -q "install ok installed"; then
        echo "Uninstalling Caddy..."
        sudo apt-get --purge remove -y caddy
        sudo apt-get autoremove -y
    fi
    [ -f "${CADDY_SOURCES_LIST}" ] && sudo rm -f "${CADDY_SOURCES_LIST}"
    [ -f "${CADDY_KEYRING}" ] && sudo rm -f "${CADDY_KEYRING}"

    local reply
    read -r -p "Remove ${SYS_DIR} (Caddyfile + deployed certs)? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] && sudo rm -rf "${SYS_DIR}"

    read -r -p "Remove the acme.sh client (root) and its renewal cron? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]] && acme_is_installed; then
        acme_root --uninstall || true
        sudo rm -rf "${ACME_HOME}"
    fi

    read -r -p "Remove service user ${CADDY_USER} and group ${WEB_GROUP}? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        if getent passwd "${CADDY_USER}" > /dev/null; then sudo userdel "${CADDY_USER}" 2>/dev/null || true; fi
        if getent group "${WEB_GROUP}" > /dev/null; then sudo groupdel "${WEB_GROUP}" 2>/dev/null || true; fi
        sudo rm -rf /var/lib/euler-caddy
    fi
    echo "Frontend uninstall complete."
}

do_status() {
    if caddy_is_installed; then
        echo "Caddy:      ✓ installed ($(caddy_bin)) — $(caddy_version)"
    else
        echo "Caddy:      ✗ not installed"
    fi
    if acme_is_installed; then
        echo "acme.sh:    ✓ installed (root) — $(acme_root --version 2>/dev/null | tail -n1)"
    else
        echo "acme.sh:    ✗ not installed"
    fi
    if sudo test -f "${CERT_FILE}"; then
        if command -v openssl &> /dev/null; then
            echo "Cert (${CERT_FILE}):"
            sudo openssl x509 -in "${CERT_FILE}" -noout -subject -enddate 2>/dev/null | sed 's/^/  /'
        else
            echo "Cert:       present (install openssl to show expiry)"
        fi
    else
        echo "Cert:       ✗ not deployed (run '$0 install')"
    fi
    if command -v systemctl &> /dev/null && [ -f "${SERVICE_DEST}" ]; then
        echo "${SERVICE_NAME}: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null)/$(systemctl is-enabled "${SERVICE_NAME}" 2>/dev/null)"
    else
        echo "${SERVICE_NAME}: ✗ not installed"
    fi
    # Health ping (resolve the domain to loopback so it works without public DNS).
    local code
    code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
        --resolve "${DOMAIN}:443:127.0.0.1" "https://${DOMAIN}/healthz" 2>/dev/null || echo '000')"
    echo "/healthz:   HTTP ${code} (expect 200)"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install "${2:-}" ;;
    uninstall) do_uninstall ;;
    upgrade)   do_upgrade ;;
    renew)     do_renew ;;
    reload)    do_reload ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac
