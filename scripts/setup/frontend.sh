#!/usr/bin/env bash
# Frontend (web edge) Setup Script — server redesign edge orchestrator
# ====================================================================
#
# Single orchestrator for the solver web edge: installs / uninstalls / upgrades
# Caddy (TLS + reverse-proxy edge) and the acme.sh cert client, creates the
# dedicated service identities, generates the Caddyfile router, deploys the static
# maintenance page, and installs the root-owned systemd unit. Supersedes the old
# scripts/setup/caddy.sh + scripts/setup/acme.sh. See docs/secure-web-server.md
# (Design decisions DD-1..DD-4, DD-6/DD-9 routing; Phases 1, 3 and 4).
#
# Topology through Phase 4:
#   - Caddy terminates TLS on :443, serves a Caddy-native health endpoint
#     (`/healthz` -> 200) and the shared static assets (`/assets/*`), routes the
#     public auth surface (/login, /register*, /reset*, /forgot, /auth/*) to the
#     auth service's unix socket, and gates every other request through the auth
#     service's forward_auth endpoint (200 + X-User/X-Profile continues; 401
#     redirects to /login). Client-supplied X-User/X-Profile are stripped (DD-9).
#     Authenticated requests are then routed **by X-Profile** to the matching
#     per-profile instance (DD-12/DD-13): /ws to euler-ws-<profile> (the terminal's
#     WebSocket, Phase 6), everything else to euler-content-<profile> (Phase 5). An
#     unknown/absent profile falls through to the static "under maintenance" holding
#     page (HTTP 503), which a handle_errors block also serves when an upstream is down.
#   - The cert is issued out-of-band by acme.sh via DNS-01 (Caddy performs no ACME).
#
# Service identity (DD-2):
#   - group  `euler-web` — the shared group whose members may reach the app sockets.
#   - user   `euler-caddy` — runs the edge; member of `euler-web`; binds :443 via
#     CAP_NET_BIND_SERVICE. (euler-auth / euler-content / euler-ws / euler-proxy are
#     created by their own phases.)
#
# Config + secrets live under /etc/euler, NOT in the repo: the dedicated service users
# cannot traverse the repo owner's 0750 home dir, so the edge is decoupled from the
# checkout. No service runs as root (DD-4): Caddy runs as euler-caddy, and acme.sh runs as
# euler-acme (home /usr/local/share/euler-acme), deploying the cert into a setgid
# /etc/euler/tls and reloading Caddy via its admin API (`caddy reload`). Renewal runs on
# euler-acme.timer. ~/.euler/env is the authoring source; the installer deploys scoped runtime
# config into /etc/euler.
#
#   /etc/euler/Caddyfile          root:euler-web       0644   (generated; non-secret)
#   /etc/euler/edge.env           root:euler-web       0644   (FQDN + email; runtime config)
#   /etc/euler/web-content/       root:euler-web       0755   (deployed static maintenance page)
#   /etc/euler/tls/               euler-acme:euler-web 2750   (setgid)
#   /etc/euler/tls/server.crt     euler-acme:euler-web 0644
#   /etc/euler/tls/server.key     euler-acme:euler-web 0640   (readable by euler-caddy via group)
#   euler-caddy.service · euler-acme.service + .timer   (root-owned, boot-enabled)
#
# The deployment FQDN is the single source of truth in the project env file ~/.euler/env
# (`EULER_TLS_DOMAIN=...`); install / upgrade / renew / status all read it from there
# and fail if it is unset. The Caddyfile is regenerated from it on install/upgrade.
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

# ── Static web content (Phase 3 maintenance page + assets) ────────────────────────
# Authored in the repo, deployed under /etc/euler because euler-caddy cannot read the
# repo owner's 0750 home dir (DD-3 config-location rationale).
WEB_CONTENT_SRC="${PROJECT_ROOT}/solver/web/content"   # repo source of truth
WEB_CONTENT_DIR="${SYS_DIR}/web-content"               # deployed, readable by euler-caddy

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

# ── acme.sh, installed and run as the dedicated euler-acme user (DD-4) ─────────────
ACME_USER="euler-acme"
ACME_GROUP="euler-acme"
ACME_HOME="/usr/local/share/euler-acme"    # acme.sh working/config dir, owned by euler-acme
ACME_BIN="${ACME_HOME}/acme.sh"
ACME_INSTALL_URL="https://get.acme.sh"
ACME_SERVICE="euler-acme.service"          # oneshot: acme.sh --cron (renewal)
ACME_TIMER="euler-acme.timer"              # daily renewal trigger
ACME_SERVICE_DEST="/etc/systemd/system/${ACME_SERVICE}"
ACME_TIMER_DEST="/etc/systemd/system/${ACME_TIMER}"

# ── Config ────────────────────────────────────────────────────────────────────────
ENV_FILE="$(dirname "${PROJECT_ROOT}")/.$(basename "${PROJECT_ROOT}")/env"       # authoring source of truth: FQDN + DNS creds
EDGE_ENV="${SYS_DIR}/edge.env"             # deployed runtime config (FQDN + email), non-secret
DOMAIN=""                                  # the deployment FQDN (load_fqdn)
ACME_EMAIL="${EULER_TLS_EMAIL:-vikas.munshi@gmail.com}"
DNS_PROVIDER="${EULER_TLS_DNS_PROVIDER:-namecom}"

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|upgrade|redeploy|status|renew|reload|help]

  install    Full edge setup: create euler-web group + euler-caddy user, install
             Caddy + acme.sh, generate /etc/euler/Caddyfile for the FQDN from ~/.euler/env
             (EULER_TLS_DOMAIN), issue+deploy the cert, and install the root-owned
             ${SERVICE_NAME} (boot-enabled).
  uninstall  Remove the unit and Caddy; prompt before deleting /etc/euler, acme.sh,
             and the service users/group.
  upgrade    Upgrade Caddy + acme.sh and regenerate the Caddyfile + unit.
  redeploy   Fast path: re-copy the static web-content (assets + vendor), regenerate
             the Caddyfile (picking up route changes), validate, and reload — no
             package upgrade, cert, or unit changes.
  status     Show install state, cert expiry, unit state, and a /healthz ping.
  renew      Force-renew the certificate now (as root; creds cached by acme.sh).
  reload     Reload the running edge (sudo systemctl reload).

  The deployment FQDN is read from ~/.euler/env (EULER_TLS_DOMAIN); commands fail if unset.
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

# Load the deployment FQDN (+ email) into $DOMAIN. Prefers the deployed runtime config
# /etc/euler/edge.env; falls back to the repo authoring source ~/.euler/env (for a first
# install). Fails if EULER_TLS_DOMAIN is set in neither.
load_fqdn() {
    local src=""
    if [ -r "${EDGE_ENV}" ]; then
        src="${EDGE_ENV}"
    elif [ -f "${ENV_FILE}" ]; then
        src="${ENV_FILE}"
    fi
    if [ -n "${src}" ]; then
        set -a
        # shellcheck disable=SC1090
        . "${src}"
        set +a
    fi
    DOMAIN="${EULER_TLS_DOMAIN:-}"
    ACME_EMAIL="${EULER_TLS_EMAIL:-${ACME_EMAIL}}"
    if [ -z "${DOMAIN}" ]; then
        echo "Error: EULER_TLS_DOMAIN is not set in ${EDGE_ENV} or ${ENV_FILE}" >&2
        echo "       Add a line like:  EULER_TLS_DOMAIN=euler.example.com" >&2
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
    # euler-caddy — the edge, in euler-web. (euler-auth / euler-content / euler-ws /
    # euler-proxy are created by their own phases.)
    if ! getent passwd "${CADDY_USER}" > /dev/null; then
        echo "Creating system user ${CADDY_USER} (group ${WEB_GROUP})..."
        sudo useradd --system --no-create-home --shell /usr/sbin/nologin \
            -g "${WEB_GROUP}" "${CADDY_USER}"
    else
        sudo usermod -g "${WEB_GROUP}" "${CADDY_USER}" || true
    fi
    # euler-acme — runs acme.sh, own group, home in /usr/local/share (DD-4, not root).
    if ! getent group "${ACME_GROUP}" > /dev/null; then
        sudo groupadd --system "${ACME_GROUP}"
    fi
    if ! getent passwd "${ACME_USER}" > /dev/null; then
        echo "Creating system user ${ACME_USER}..."
        sudo useradd --system --home-dir "${ACME_HOME}" --shell /usr/sbin/nologin \
            -g "${ACME_GROUP}" "${ACME_USER}"
    fi
}

ensure_sys_dirs() {
    # /etc/euler is 0755 so euler-acme (outside euler-web) can traverse to its tls dir;
    # the sensitive files inside carry their own perms. tls/ is setgid euler-web (2750),
    # so certs euler-acme writes there inherit group euler-web for euler-caddy to read.
    sudo install -d -o root -g "${WEB_GROUP}" -m 0755 "${SYS_DIR}"
    sudo install -d -o "${ACME_USER}" -g "${WEB_GROUP}" -m 2750 "${TLS_DIR}"
    sudo install -d -o "${ACME_USER}" -g "${ACME_GROUP}" -m 0750 "${ACME_HOME}"
}

# Deploy the non-secret runtime config the services read instead of the repo (DD-4).
deploy_edge_env() {
    sudo tee "${EDGE_ENV}" > /dev/null <<EOF
# GENERATED by scripts/setup/frontend.sh — deployed runtime config (non-secret).
# Authoring source: ~/.euler/env. Read by frontend.sh (FQDN) and the euler services.
EULER_TLS_DOMAIN=${DOMAIN}
EULER_TLS_EMAIL=${ACME_EMAIL}
EOF
    sudo chown root:"${WEB_GROUP}" "${EDGE_ENV}"
    sudo chmod 0644 "${EDGE_ENV}"
}

# Deploy the static web content (Phase 3 maintenance page + assets) from the repo into
# /etc/euler/web-content, where euler-caddy can read it. Fully replaced each run so the
# deployed tree mirrors the repo source; non-secret, so root:euler-web 0644/0755.
deploy_web_content() {
    if [ ! -d "${WEB_CONTENT_SRC}" ]; then
        echo "Warning: ${WEB_CONTENT_SRC} not found; skipping static content deploy" >&2
        return 0
    fi
    echo "Deploying static web content to ${WEB_CONTENT_DIR}..."
    sudo rm -rf "${WEB_CONTENT_DIR}"
    sudo cp -r "${WEB_CONTENT_SRC}" "${WEB_CONTENT_DIR}"
    sudo chown -R root:"${WEB_GROUP}" "${WEB_CONTENT_DIR}"
    sudo find "${WEB_CONTENT_DIR}" -type d -exec chmod 0755 {} +
    sudo find "${WEB_CONTENT_DIR}" -type f -exec chmod 0644 {} +
}

# ── acme.sh (as root) ─────────────────────────────────────────────────────────────

acme_is_installed() { sudo test -x "${ACME_BIN}"; }

# Run acme.sh as the euler-acme user (DD-4). acme.sh refuses to run under a bare `sudo`
# (it detects the SUDO_* env vars), so strip those markers and pin HOME to its working
# dir. For calls needing extra environment (the DNS credentials at issue time) use
# acme_run_with_creds, which prepends the $cred_env `VAR=val` pairs before the binary.
#
# LE_WORKING_DIR is pinned to ACME_HOME because we install with `--home ${ACME_HOME}`
# (everything directly in that dir, not the stock `$HOME/.acme.sh` subdir). Most
# subcommands re-derive it from the script's own location, but `--upgrade` falls back
# to `$HOME/.acme.sh` when it is unset — a dir that does not exist here, so the upgrade
# `cd`s nowhere, then tries to download the tarball into the launch CWD (which euler-acme
# cannot write) and fails with a "Permission denied". Setting it explicitly matches the
# install layout for every call.
ACME_CLEAN_ENV=(env -u SUDO_COMMAND -u SUDO_USER -u SUDO_UID -u SUDO_GID \
    "HOME=${ACME_HOME}" "LE_CONFIG_HOME=${ACME_HOME}" "LE_WORKING_DIR=${ACME_HOME}")
acme_run() {
    sudo -u "${ACME_USER}" "${ACME_CLEAN_ENV[@]}" "${ACME_BIN}" "$@"
}
acme_run_with_creds() {
    sudo -u "${ACME_USER}" "${ACME_CLEAN_ENV[@]}" "${cred_env[@]}" "${ACME_BIN}" "$@"
}

install_acme() {
    if ! command -v curl &> /dev/null; then
        echo "Error: curl is required to install acme.sh" >&2
        return 1
    fi
    if acme_is_installed; then
        echo "acme.sh already installed (${ACME_USER}): $(acme_run --version 2>/dev/null | tail -n1)"
    else
        echo "Installing acme.sh as ${ACME_USER} (into ${ACME_HOME})..."
        # Run the installer *from* ACME_HOME: its bootstrap downloads the tarball into the
        # CWD, and euler-acme cannot write to the repo the operator launched this from.
        # get.acme.sh treats its FIRST positional as an `email=` token (it prepends `--`),
        # so pass `email=...` first, then the install flags.
        sudo -u "${ACME_USER}" env "HOME=${ACME_HOME}" sh -c \
            "cd '${ACME_HOME}' && curl -fsSL '${ACME_INSTALL_URL}' | sh -s -- email='${ACME_EMAIL}' --home '${ACME_HOME}' --config-home '${ACME_HOME}' --nocron"
    fi
    acme_run --set-default-ca --server letsencrypt
    # Migrate off any prior root install so renewals don't run twice (clean-root env —
    # acme.sh refuses a bare sudo).
    if sudo test -x /root/.acme.sh/acme.sh; then
        echo "Removing the superseded root acme.sh cron..."
        sudo env -u SUDO_COMMAND -u SUDO_USER -u SUDO_UID -u SUDO_GID HOME=/root \
            /root/.acme.sh/acme.sh --uninstall 2>/dev/null || true
    fi
    echo "acme.sh ready (default CA: Let's Encrypt)"
}

# Resolve $DNS_PROVIDER to its acme.sh hook (into $DNS_HOOK) and the required credential
# variable names (into the $REQUIRED array), loading values from ~/.euler/env (read as the
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

    # Reload command re-run by euler-acme on every renewal: ensure the key stays
    # group-readable (setgid gives the euler-web group) and reload Caddy via its admin
    # API — no root, no systemctl. Best effort: on first issue the edge is not up yet.
    local caddy reload_cmd
    caddy="$(caddy_bin)"
    reload_cmd="chmod 0640 ${KEY_FILE}; chmod 0644 ${CERT_FILE}; ${caddy} reload --config ${CADDYFILE} 2>/dev/null || true"

    echo "Issuing certificate for ${DOMAIN} via ${DNS_PROVIDER} DNS-01 (${DNS_HOOK})..."
    local rc=0
    acme_run_with_creds --issue --dns "${DNS_HOOK}" -d "${DOMAIN}" --server letsencrypt || rc=$?
    # exit code 2 = "skipped, still valid" — success for our purposes.
    if [ "${rc}" -ne 0 ] && [ "${rc}" -ne 2 ]; then
        echo "Error: certificate issuance failed (acme.sh exit ${rc})" >&2
        return "${rc}"
    fi

    # Clear any stale cert from a prior (root) deploy so euler-acme can write fresh files:
    # it owns the dir (can create/delete) but cannot overwrite root-owned files in place.
    sudo rm -f "${CERT_FILE}" "${KEY_FILE}"
    echo "Deploying certificate to ${TLS_DIR}..."
    acme_run --install-cert -d "${DOMAIN}" \
        --fullchain-file "${CERT_FILE}" \
        --key-file "${KEY_FILE}" \
        --reloadcmd "${reload_cmd}"
    if ! sudo test -f "${CERT_FILE}" || ! sudo test -f "${KEY_FILE}"; then
        echo "Error: cert/key were not installed" >&2
        return 1
    fi
    # euler-acme owns them and the setgid dir gave them group euler-web; just fix modes.
    sudo chmod 0644 "${CERT_FILE}"
    sudo chmod 0640 "${KEY_FILE}"
    echo "Deployed cert -> ${CERT_FILE} (${ACME_USER}:${WEB_GROUP} 0644)"
    echo "Deployed key  -> ${KEY_FILE} (${ACME_USER}:${WEB_GROUP} 0640)"
}

# ── Caddyfile router (Phase 1) ────────────────────────────────────────────────────

generate_caddyfile() {
    echo "Writing ${CADDYFILE} for ${DOMAIN}..."
    sudo tee "${CADDYFILE}" > /dev/null <<EOF
# Caddy configuration for the solver web edge (Phase 4).
#
# GENERATED by scripts/setup/frontend.sh — edits are overwritten on install/upgrade.
# Caddy terminates TLS, serves the health endpoint + static assets, routes the
# public auth surface to the auth service (unix //run/euler/auth.sock), and gates
# every other request through the auth service's forward_auth endpoint (DD-6/DD-9):
# 200 + X-User/X-Profile continues downstream, 401 redirects to /login. Until the
# content service lands (Phase 5), authenticated requests fall through to the
# static maintenance holding page (from ${WEB_CONTENT_DIR}), which also serves
# whenever an upstream is down. The cert is issued out-of-band by acme.sh (DNS-01)
# into ${TLS_DIR}; Caddy loads it via \`tls\` and performs no ACME itself.
{
	# DNS-01 needs no inbound :80, so keep Caddy off :80 (no HTTP->HTTPS redirect).
	auto_https disable_redirects
}

# Transport-level security headers + edge fallback CSP, shared by the live routes and
# the maintenance/error responses. The CSP uses the '?' (set-if-absent) operator so it
# is only a **fallback**: the app tier mints a per-response, nonce'd CSP with the
# exceptions its pages need (style-src 'unsafe-inline' for MathJax/CodeMirror injected
# styles; frame-ancestors 'self' for the terminal iframe — docs/secure-web-server.md
# §4.7), and Caddy leaves that untouched. This strict policy applies only to
# Caddy-native responses (maintenance / static / redirects) that carry no app CSP.
# (docs/secure-web-server.md, docs/security-assessment.md SEC-04/SEC-05.)
(security_headers) {
	header {
		Strict-Transport-Security "max-age=31536000; includeSubDomains"
		X-Content-Type-Options "nosniff"
		Referrer-Policy "no-referrer"
		?Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
		-Server
	}
}

# Reusable holding page: serve the static maintenance HTML with 503 Service
# Unavailable + Retry-After. Its stylesheet under /assets is served (200) by the
# route below, so the page renders styled even while the site is "down".
(maintenance) {
	root * ${WEB_CONTENT_DIR}
	rewrite * /maintenance.html
	file_server {
		status 503
	}
	header Content-Type "text/html; charset=utf-8"
	header Retry-After "3600"
}

${DOMAIN} {
	tls ${CERT_FILE} ${KEY_FILE}
	import security_headers

	# DD-9: identity headers reach the app tier ONLY as copies of the forward_auth
	# response — anything a client sends is stripped before any routing happens.
	request_header -X-User
	request_header -X-Profile

	# Per-profile content routing (DD-12): matchers on the X-Profile that
	# forward_auth returns, used to pick the matching per-profile content instance
	# below. Defined at site scope, evaluated where referenced (after forward_auth
	# has set the header). admin is local-only; the web ladder caps at maintainer.
	@content_reader header X-Profile reader
	@content_contributor header X-Profile contributor
	@content_maintainer header X-Profile maintainer

	# The web shell (Phase 6, DD-13): /ws goes to the per-profile euler-ws instance,
	# same X-Profile split. Every web rung gets a terminal — attach is solver:execute,
	# a reader grant — and what the shell inside it may run is the DD-12 decorator's
	# call, not the edge's. Caddy proxies the WebSocket upgrade natively.
	@ws_reader {
		path /ws
		header X-Profile reader
	}
	@ws_contributor {
		path /ws
		header X-Profile contributor
	}
	@ws_maintainer {
		path /ws
		header X-Profile maintainer
	}

	# Health probe — Caddy-native, no upstream.
	handle /healthz {
		respond "ok" 200
	}

	# Static assets (the auth pages' CSS/JS, srp.js, terms, maintenance styling),
	# served same-origin so the CSP 'self' policy covers them.
	handle /assets/* {
		root * ${WEB_CONTENT_DIR}
		file_server
	}

	# Vendored front-end libraries (htmx, MathJax + its fonts) — Caddy-native,
	# same-origin, per the site-design path-ownership table.
	handle /vendor/* {
		root * ${WEB_CONTENT_DIR}
		file_server
	}

	# Public auth surface (DD-7): the login/registration/reset/forgot pages and
	# the JSON auth API, straight to the auth service. The shell-ticket and admin
	# endpoints are deliberately NOT routed (socket-peer / local-only, DD-6/DD-9).
	handle /login {
		reverse_proxy unix//run/euler/auth.sock
	}
	handle /register* {
		reverse_proxy unix//run/euler/auth.sock
	}
	handle /reset* {
		reverse_proxy unix//run/euler/auth.sock
	}
	handle /forgot {
		reverse_proxy unix//run/euler/auth.sock
	}
	handle /password {
		reverse_proxy unix//run/euler/auth.sock
	}
	handle /terms {
		reverse_proxy unix//run/euler/auth.sock
	}
	handle /auth/* {
		reverse_proxy unix//run/euler/auth.sock
	}

	# Everything else requires an authenticated session (DD-6): the auth service
	# answers 200 + X-User/X-Profile (copied onto the proxied request) or 401,
	# which becomes a redirect to the login page. route{} preserves written order —
	# forward_auth runs first (setting X-Profile or 401→redirect), then the first
	# matching per-profile content upstream proxies, else the holding page.
	handle {
		route {
			forward_auth unix//run/euler/auth.sock {
				uri /auth/check
				copy_headers X-User X-Profile
				@unauthed status 401
				handle_response @unauthed {
					redir * /login 302
				}
			}

			# Phase 6 (DD-13): the terminal's WebSocket, to the matching per-profile
			# euler-ws instance. Matched *before* the content routes, since /ws is a
			# path both would otherwise claim.
			reverse_proxy @ws_maintainer unix//run/euler/ws-maintainer.sock
			reverse_proxy @ws_contributor unix//run/euler/ws-contributor.sock
			reverse_proxy @ws_reader unix//run/euler/ws-reader.sock

			# Phase 5 (DD-12): route by the profile forward_auth returned to the
			# matching per-profile content instance, each its own euler-content-<p>
			# uid + socket. An unknown/absent profile falls through to maintenance.
			reverse_proxy @content_maintainer unix//run/euler/content-maintainer.sock
			reverse_proxy @content_contributor unix//run/euler/content-contributor.sock
			reverse_proxy @content_reader unix//run/euler/content-reader.sock

			# No profile matched (or the content instance is unset) → holding page.
			import maintenance
		}
	}

	# When a later-phase upstream reverse_proxy fails, serve the same holding page
	# instead of a bare 502/504.
	handle_errors {
		import maintenance
	}
}
EOF
    sudo chown root:"${WEB_GROUP}" "${CADDYFILE}"
    sudo chmod 0644 "${CADDYFILE}"          # non-secret; euler-acme reads it for `caddy reload`
}

# Validate the Caddyfile (as root, so it can read the 0640 key).
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
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/secure-web-server.md
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

# Root-owned systemd timer that runs `acme.sh --cron` as euler-acme (DD-4) — replaces
# acme.sh's own user crontab (installed with --nocron).
install_acme_timer() {
    require_systemd || return 1
    echo "Installing ${ACME_TIMER} (daily renewal as ${ACME_USER})..."
    sudo tee "${ACME_SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler certificate renewal (acme.sh --cron)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/secure-web-server.md
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=${ACME_USER}
Group=${ACME_GROUP}
Environment=HOME=${ACME_HOME}
Environment=LE_CONFIG_HOME=${ACME_HOME}
ExecStart=${ACME_BIN} --cron --home ${ACME_HOME} --config-home ${ACME_HOME}
EOF
    sudo tee "${ACME_TIMER_DEST}" > /dev/null <<EOF
[Unit]
Description=Daily euler certificate renewal check

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable --now "${ACME_TIMER}"
}

remove_acme_units() {
    local u
    for u in "${ACME_TIMER}" "${ACME_SERVICE}"; do
        if [ -f "/etc/systemd/system/${u}" ]; then
            sudo systemctl disable --now "${u}" 2>/dev/null || true
            sudo rm -f "/etc/systemd/system/${u}"
        fi
    done
    sudo systemctl daemon-reload
}

# ── Actions ───────────────────────────────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    load_fqdn || return 1

    install_caddy_pkg
    ensure_group_and_users
    ensure_sys_dirs
    deploy_edge_env
    deploy_web_content
    generate_caddyfile
    install_acme
    issue_cert
    install_service
    install_acme_timer
    echo "Frontend edge setup complete for ${DOMAIN}."
    do_status || true
}

do_upgrade() {
    check_can_sudo || return 1
    require_systemd || return 1
    load_fqdn || return 1

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
        acme_run --upgrade || true
    fi
    ensure_group_and_users
    ensure_sys_dirs
    deploy_edge_env
    deploy_web_content                 # refresh the static maintenance page + assets
    generate_caddyfile                 # regenerate from the FQDN
    install_service                    # re-lay the unit and reload
    install_acme_timer
    echo "Frontend upgrade complete: $(caddy_version)"
}

do_renew() {
    check_can_sudo || return 1
    load_fqdn || return 1
    if ! acme_is_installed; then
        echo "Error: acme.sh is not installed (root); run '$0 install' first." >&2
        return 1
    fi
    echo "Renewing certificate for ${DOMAIN} (force)..."
    acme_run --renew -d "${DOMAIN}" --force
    echo "Renewal complete for ${DOMAIN}"
}

do_reload() {
    check_can_sudo || return 1
    sudo systemctl reload "${SERVICE_NAME}"
    echo "Reloaded ${SERVICE_NAME}"
}

# Fast redeploy: push the repo's static web-content + regenerated Caddyfile to the
# running edge, then reload. No package upgrade, cert issuance, or unit re-lay — the
# common "I changed CSS/JS/vendor or a Caddy route" turnaround.
do_redeploy() {
    check_can_sudo || return 1
    load_fqdn || return 1
    if ! sudo test -f "${CERT_FILE}"; then
        echo "Error: edge not installed (no cert at ${CERT_FILE}); run '$0 install' first." >&2
        return 1
    fi
    deploy_web_content
    generate_caddyfile
    if ! validate_caddyfile; then
        echo "Error: generated Caddyfile failed validation; not reloading." >&2
        return 1
    fi
    do_reload
    echo "Frontend redeploy complete: web-content + Caddyfile refreshed and reloaded."
}

do_uninstall() {
    check_can_sudo || return 1
    remove_service
    remove_acme_units

    if dpkg-query -W -f='${Status}' caddy 2>/dev/null | grep -q "install ok installed"; then
        echo "Uninstalling Caddy..."
        sudo apt-get --purge remove -y caddy
        sudo apt-get autoremove -y
    fi
    [ -f "${CADDY_SOURCES_LIST}" ] && sudo rm -f "${CADDY_SOURCES_LIST}"
    [ -f "${CADDY_KEYRING}" ] && sudo rm -f "${CADDY_KEYRING}"

    local reply
    read -r -p "Remove ${SYS_DIR} (Caddyfile + deployed certs + edge.env)? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] && sudo rm -rf "${SYS_DIR}"

    read -r -p "Remove the acme.sh client (${ACME_HOME})? [y/N] " reply
    [[ "${reply}" =~ ^[Yy]$ ]] && sudo rm -rf "${ACME_HOME}"

    read -r -p "Remove service users (${CADDY_USER}, ${ACME_USER}) and group ${WEB_GROUP}? [y/N] " reply
    if [[ "${reply}" =~ ^[Yy]$ ]]; then
        local u
        for u in "${CADDY_USER}" "${ACME_USER}"; do
            if getent passwd "${u}" > /dev/null; then sudo userdel "${u}" 2>/dev/null || true; fi
        done
        if getent group "${ACME_GROUP}" > /dev/null; then sudo groupdel "${ACME_GROUP}" 2>/dev/null || true; fi
        if getent group "${WEB_GROUP}" > /dev/null; then sudo groupdel "${WEB_GROUP}" 2>/dev/null || true; fi
        sudo rm -rf /var/lib/euler-caddy
    fi
    echo "Frontend uninstall complete."
}

do_status() {
    load_fqdn || return 1
    if caddy_is_installed; then
        echo "Caddy:      ✓ installed ($(caddy_bin)) — $(caddy_version)"
    else
        echo "Caddy:      ✗ not installed"
    fi
    if acme_is_installed; then
        echo "acme.sh:    ✓ installed (${ACME_USER}) — $(acme_run --version 2>/dev/null | tail -n1)"
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
    # Auto-renewal (DD-4): euler-acme.timer runs `acme.sh --cron` as euler-acme daily;
    # show its state and the next scheduled renewal (ARI window before expiry).
    if [ -f "${ACME_TIMER_DEST}" ] && command -v systemctl &> /dev/null; then
        local next
        next="$(acme_run --info -d "${DOMAIN}" 2>/dev/null | sed -n 's/^Le_NextRenewTimeStr=//p' | tr -d "\"'")"
        echo "Renewal:    ${ACME_TIMER} $(systemctl is-active "${ACME_TIMER}" 2>/dev/null)/$(systemctl is-enabled "${ACME_TIMER}" 2>/dev/null)${next:+ — next: ${next}}"
    else
        echo "Renewal:    ✗ ${ACME_TIMER} not installed"
    fi
    if command -v systemctl &> /dev/null && [ -f "${SERVICE_DEST}" ]; then
        echo "${SERVICE_NAME}: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null)/$(systemctl is-enabled "${SERVICE_NAME}" 2>/dev/null)"
    else
        echo "${SERVICE_NAME}: ✗ not installed"
    fi
    # Health ping (resolve the domain to loopback so it works without public DNS).
    # curl's -w prints 000 on failure; capture it (|| true) instead of appending another.
    local code
    code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
        --resolve "${DOMAIN}:443:127.0.0.1" "https://${DOMAIN}/healthz" 2>/dev/null || true)"
    echo "/healthz:   HTTP ${code:-000} (expect 200)"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install ;;
    uninstall) do_uninstall ;;
    upgrade)   do_upgrade ;;
    redeploy)  do_redeploy ;;
    renew)     do_renew ;;
    reload)    do_reload ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac
