#!/usr/bin/env bash
# acme.sh Setup Script (TLS certificate issuance for solver-web)
# ==============================================================
#
# Installs the acme.sh ACME client and issues/renews the Let's Encrypt certificate
# for the solver-web HTTPS front end using the name.com DNS-01 challenge, then
# deploys the cert into keys/ where Caddy loads it (see docs/tls-setup.md).
#
# Why acme.sh: Caddy's own name.com DNS plugin (caddy-dns/namedotcom) is
# unmaintained and no longer builds, so DNS-01 issuance is delegated to acme.sh,
# whose `dns_namecom` client works with the name.com API. Stock Caddy just loads
# the resulting cert (installed via scripts/setup/caddy.sh).
#
# acme.sh installs under ~/.acme.sh (no sudo needed) and adds a cron entry that
# auto-renews and re-runs the reload command below.
#
# name.com API credentials are read from the project .env (the same file that holds
# ANTHROPIC_API_KEY), as:
#     NAMEDOTCOM_USERNAME=<username>
#     NAMEDOTCOM_TOKEN=<token>
# or from the existing environment if already exported. acme.sh caches them after
# the first issue, so renewals need no re-entry.
#
# Features:
# - Installs acme.sh (idempotent) and defaults its CA to Let's Encrypt
# - Issues the cert via name.com DNS-01 and deploys it to keys/ (mode 600 key)
# - Reloads Caddy on issue and on every auto-renewal
# - Force-renews on demand; reports status; uninstalls the client cleanly
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

# Project root, derived from this script's location (scripts/setup/acme.sh), so the
# cert deploy paths resolve regardless of the caller's current directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ACME_HOME="${HOME}/.acme.sh"
ACME_BIN="${ACME_HOME}/acme.sh"
ACME_INSTALL_URL="https://get.acme.sh"

# Overridable via the environment.
DOMAIN="${EULER_TLS_DOMAIN:-euler.vikasmunshi.com}"
ACME_EMAIL="${EULER_TLS_EMAIL:-vikas.munshi@gmail.com}"

CERT_FILE="${PROJECT_ROOT}/keys/.server.crt"    # full chain; gitignored dotfile
KEY_FILE="${PROJECT_ROOT}/keys/.server.key"     # private key; gitignored dotfile
ENV_FILE="${PROJECT_ROOT}/.env"                 # name.com creds (NAMEDOTCOM_USERNAME / NAMEDOTCOM_TOKEN)
CADDYFILE="${PROJECT_ROOT}/Caddyfile"

# Reload Caddy over its admin API (no sudo); on first issue Caddy may not yet be
# running, in which case the reload is a harmless no-op and the cert still deploys.
RELOAD_CMD="${EULER_TLS_RELOAD_CMD:-caddy reload --config ${CADDYFILE}}"

usage() {
    echo "Usage: $0 [install|issue|renew|uninstall|status]"
    echo
    echo "  install    Install the acme.sh client (default)"
    echo "  issue      Issue the cert via name.com DNS-01 and deploy it to keys/"
    echo "  renew      Force-renew the cert now (credentials cached by acme.sh)"
    echo "  uninstall  Remove the acme.sh client and its renewal cron"
    echo "  status     Show client version, issued domains, and cert expiry"
}

# Returns 0 if acme.sh is installed, 1 otherwise.
acme_is_installed() {
    [ -x "${ACME_BIN}" ]
}

# Installs acme.sh (idempotent) and points its default CA at Let's Encrypt.
install_acme() {
    if ! command -v curl &> /dev/null; then
        echo "Error: curl is required to install acme.sh" >&2
        return 1
    fi
    if acme_is_installed; then
        echo "acme.sh already installed: $(${ACME_BIN} --version 2>/dev/null | tail -n1)"
    else
        echo "Installing acme.sh..."
        curl -fsSL "${ACME_INSTALL_URL}" | sh -s "email=${ACME_EMAIL}"
    fi
    "${ACME_BIN}" --set-default-ca --server letsencrypt
    echo "acme.sh ready (default CA: Let's Encrypt)"
}

# Loads name.com credentials into the environment for acme.sh, from the project
# .env if present, else from the existing environment. Errors if either is missing.
load_namecom_creds() {
    if [ -f "${ENV_FILE}" ]; then
        # shellcheck disable=SC1090
        set -a; . "${ENV_FILE}"; set +a
    fi
    if [ -z "${NAMEDOTCOM_USERNAME:-}" ] || [ -z "${NAMEDOTCOM_TOKEN:-}" ]; then
        echo "Error: name.com credentials not found." >&2
        echo "Add them to ${ENV_FILE} (or export them):" >&2
        echo "    NAMEDOTCOM_USERNAME=<username>" >&2
        echo "    NAMEDOTCOM_TOKEN=<token>" >&2
        return 1
    fi
    Namecom_Username=${NAMEDOTCOM_USERNAME}
    Namecom_Token=${NAMEDOTCOM_TOKEN}
    export Namecom_Username Namecom_Token
}

# Deploys the issued cert into keys/ and registers the reload command. acme.sh
# re-runs the reload command on every future auto-renewal.
deploy_cert() {
    # acme.sh installs the cert/key *before* running the reload command, so a reload
    # failure (e.g. Caddy not running yet / no Caddyfile on first setup) still leaves
    # a good cert on disk. Capture the status rather than letting `set -e` abort, so
    # the key is always chmod'd and the outcome is reported clearly.
    local rc=0
    "${ACME_BIN}" --install-cert -d "${DOMAIN}" \
        --fullchain-file "${CERT_FILE}" \
        --key-file "${KEY_FILE}" \
        --reloadcmd "${RELOAD_CMD}" || rc=$?
    if [ ! -f "${CERT_FILE}" ] || [ ! -f "${KEY_FILE}" ]; then
        echo "Error: cert/key were not installed (acme.sh exit ${rc})" >&2
        return 1
    fi
    chmod 600 "${KEY_FILE}"
    echo "Deployed cert -> ${CERT_FILE}"
    echo "Deployed key  -> ${KEY_FILE} (mode 600)"
    if [ "${rc}" -ne 0 ]; then
        echo "Note: cert deployed, but the reload command failed (exit ${rc}) — expected if" >&2
        echo "      Caddy is not running yet. Caddy will pick up the cert once started, or" >&2
        echo "      reload it now with:  ${RELOAD_CMD}" >&2
    fi
}

# Issues the certificate via the name.com DNS-01 challenge, then deploys it.
issue_cert() {
    if ! acme_is_installed; then
        echo "acme.sh is not installed; installing first..."
        install_acme
    fi
    load_namecom_creds || return 1

    echo "Issuing certificate for ${DOMAIN} via name.com DNS-01..."
    # --issue is a no-op if a valid cert already exists; acme.sh exit code 2 means
    # "skipped, still valid", which is success for our purposes.
    local rc=0
    "${ACME_BIN}" --issue --dns dns_namecom -d "${DOMAIN}" || rc=$?
    if [ "${rc}" -ne 0 ] && [ "${rc}" -ne 2 ]; then
        echo "Error: certificate issuance failed (acme.sh exit ${rc})" >&2
        return "${rc}"
    fi
    deploy_cert
    echo "Certificate issue/deploy completed for ${DOMAIN}"
}

# Force-renews the certificate now (credentials are cached by acme.sh).
renew_cert() {
    if ! acme_is_installed; then
        echo "Error: acme.sh is not installed; run '$0 install' then '$0 issue'" >&2
        return 1
    fi
    load_namecom_creds || return 1
    echo "Renewing certificate for ${DOMAIN}..."
    "${ACME_BIN}" --renew -d "${DOMAIN}" --force
    echo "Renewal completed for ${DOMAIN}"
}

# Removes the acme.sh client and its cron entry (deployed certs are left in place).
uninstall_acme() {
    if ! acme_is_installed; then
        echo "acme.sh does not appear to be installed"
        return 0
    fi
    echo "Removing acme.sh client and its renewal cron..."
    "${ACME_BIN}" --uninstall || true
    if [ -d "${ACME_HOME}" ]; then
        read -r -p "Also remove ${ACME_HOME} (issued certs + account)? [y/N] " reply
        if [[ "${reply}" =~ ^[Yy]$ ]]; then
            rm -rf "${ACME_HOME}"
            echo "Removed ${ACME_HOME}"
        else
            echo "Keeping ${ACME_HOME}"
        fi
    fi
    echo "acme.sh uninstallation completed (deployed certs in keys/ left untouched)"
}

# Reports client version, issued domains, and the deployed cert's expiry.
status_acme() {
    if acme_is_installed; then
        echo "acme.sh: ✓ installed ($(${ACME_BIN} --version 2>/dev/null | tail -n1))"
        echo "Issued certificates:"
        "${ACME_BIN}" --list 2>/dev/null || true
    else
        echo "acme.sh: ✗ not installed"
    fi
    echo "Deployed cert (${CERT_FILE}):"
    if [ -f "${CERT_FILE}" ]; then
        if command -v openssl &> /dev/null; then
            openssl x509 -in "${CERT_FILE}" -noout -subject -enddate 2>/dev/null \
                | sed 's/^/  /'
        else
            echo "  present (install openssl to show expiry)"
        fi
    else
        echo "  ✗ not deployed yet (run '$0 issue')"
    fi
}

# Main execution — defaults to 'status' if no argument provided.
ACTION="${1:-status}"

case "${ACTION}" in
    install)
        install_acme
        ;;
    issue)
        issue_cert
        ;;
    renew)
        renew_cert
        ;;
    uninstall)
        uninstall_acme
        ;;
    status)
        status_acme
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
