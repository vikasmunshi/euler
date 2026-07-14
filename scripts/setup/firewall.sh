#!/usr/bin/env bash
# Kernel egress firewall (nftables) — Phase 4, step 1 of the server redesign (DD-8)
# =================================================================================
#
# Installs / uninstalls the host nftables ruleset that makes "egress only via Squid"
# a *kernel* property instead of an environment-variable convention: scoped to the
# euler-* service uids, it permits loopback plus only the specific (uid, port) egress
# each service genuinely needs, then drops the rest. Sibling to frontend.sh /
# egress.sh / ddns.sh / smtp.sh; see docs/secure-web-server.md (DD-8).
#
# Model:
#   - A dedicated `table inet euler` with one egress-only (hook output) chain,
#     policy accept: non-service traffic — SSH, root, your shell — is untouched
#     (no lock-out risk); only the enumerated euler-* uids hit the final drop.
#   - ct state established/related is accepted first, so euler-caddy can answer
#     inbound public connections on :443 while still being unable to *initiate*
#     anything off-host (its NEW outbound is dropped).
#   - Relay guard: of the app tier, only euler-auth may connect to the loopback
#     mail relay (euler-smtp's listener) — a hostile euler-ws/euler-content cannot
#     use it to send mail.
#   - The ruleset is generated with *numeric* uids resolved at generation time and
#     includes only the euler-* users that exist; rerun `reload` (or the installing
#     kit runs it) after a new service user lands.
#   - This is layer 2 of DD-8; layer 1 (per-unit IPAddressDeny=any +
#     IPAddressAllow=localhost) travels with each app service's own unit.
#
#   /etc/euler/nftables.conf                   root:root 0644  (generated here)
#   /etc/systemd/system/euler-firewall.service (root-owned, boot-enabled, oneshot)
#
# Allowed egress per uid (everything else off-host is dropped for these uids):
#   euler-proxy   tcp {80,443}  — the ONLY real internet path (Squid; L7 allowlist on top)
#   euler-acme    tcp 443       — ACME + DNS-provider API
#   euler-ddns    tcp 443       — name.com API, ipify
#   euler-smtp    tcp 587       — Gmail submission (sole holder of the creds)
#   (infra uids)  udp/tcp 53    — DNS, for resolvers off-loopback
#   all euler-*   loopback      — /run/euler sockets, Squid :3128, the mail relay
#
# Actions: install | uninstall | reload | render | status | help
#
# Author: Vikas Munshi <vikas.munshi@gmail.com>
# Copyright (c) 2026. All rights reserved.
# Licensed under the MIT License.

set -euo pipefail

SYS_DIR="/etc/euler"
NFT_CONF="${SYS_DIR}/nftables.conf"
SERVICE_NAME="euler-firewall.service"
SERVICE_DEST="/etc/systemd/system/${SERVICE_NAME}"

# The mail relay's loopback port (must match smtp.sh LISTEN_ADDR).
SMTP_RELAY_PORT="8025"

# ── The euler service tier (DD-2/DD-4/DD-8) ───────────────────────────────────────
# Every euler-* uid subject to the egress drop. Generated rules include only the
# users that exist at generation time.
# Both app services run as per-profile uids (DD-12/DD-13): euler-content-<profile> and
# euler-ws-<profile>, one per web rung. resolve_uids skips names that don't exist yet,
# so listing them ahead of content.sh / ws.sh is harmless.
ALL_USERS=(euler-caddy euler-auth
           euler-content-reader euler-content-contributor euler-content-maintainer
           euler-ws-reader euler-ws-contributor euler-ws-maintainer
           euler-proxy euler-acme euler-ddns euler-smtp)
# Infra uids allowed direct DNS (the app tier resolves via loopback only).
DNS_USERS=(euler-proxy euler-acme euler-ddns euler-smtp)
# App-tier uids barred from the mail relay port (euler-auth is the one legit client).
# The web shells are RCE by design (AR-1), so they are barred from it like the rest.
RELAY_BARRED=(euler-caddy euler-proxy euler-acme euler-ddns
              euler-content-reader euler-content-contributor euler-content-maintainer
              euler-ws-reader euler-ws-contributor euler-ws-maintainer)

usage() {
    cat <<USAGE
Usage: $0 [install|uninstall|reload|render|status|help]

  install    Install nftables, generate ${NFT_CONF} and install the root-owned,
             boot-enabled ${SERVICE_NAME} (oneshot: loads the euler table).
  uninstall  Flush the euler table and remove the ruleset + unit.
  reload     Regenerate the ruleset (picking up newly created euler-* users) and
             re-apply it.
  render     Print the generated ruleset to stdout (no changes made).
  status     Show the unit state, the live rule count, and egress probes.

  The ruleset is scoped to the euler-* uids (policy accept otherwise) — SSH, root
  and interactive shells are never affected.
USAGE
}

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
        echo "Error: systemd is required for the firewall service; it is not active here." >&2
        return 1
    fi
}

ensure_deps() {
    if ! command -v nft &> /dev/null; then
        echo "Installing nftables..."
        sudo apt-get install -y nftables
    fi
}

# Resolve an existing subset of the given user names to "uid, uid, ..." (numeric,
# comment-stable). Echoes nothing if none exist.
resolve_uids() {
    local name uid out=()
    for name in "$@"; do
        if uid="$(id -u "${name}" 2>/dev/null)"; then
            out+=("${uid}")
        fi
    done
    local IFS=', '
    echo "${out[*]-}"
}

# Same, but echo "name(uid) ..." for the header comment.
describe_uids() {
    local name uid out=()
    for name in "$@"; do
        if uid="$(id -u "${name}" 2>/dev/null)"; then
            out+=("${name}(${uid})")
        fi
    done
    echo "${out[*]-}"
}

uid_of() { id -u "$1" 2>/dev/null || true; }

# The per-user web tier (MT-7) creates euler-user-<slug> uids dynamically at provision
# time, so they cannot be listed ahead of time like the fixed service uids. Enumerate
# whatever exists now by the euler-user- prefix, so a reload after each provision folds
# the new uid into the egress drop (chain policy is accept — an unlisted uid would reach
# the internet directly, bypassing Squid). They are RCE-by-design (AR-1), so they are
# also barred from the mail relay, exactly like the euler-ws-* rungs they replace.
euler_user_names() { getent passwd | awk -F: '/^euler-user-/{print $1}'; }

# Generate the ruleset to stdout. Uses the declare-then-flush pattern so re-applying
# with `nft -f` is idempotent.
render_conf() {
    local all_uids dns_uids barred_uids per_user
    # Read the dynamic per-user uids (euler-user-<slug>) once; they join both the egress
    # drop and the relay bar alongside the fixed service uids.
    mapfile -t per_user < <(euler_user_names)
    all_uids="$(resolve_uids "${ALL_USERS[@]}" "${per_user[@]}")"
    dns_uids="$(resolve_uids "${DNS_USERS[@]}")"
    barred_uids="$(resolve_uids "${RELAY_BARRED[@]}" "${per_user[@]}")"
    if [ -z "${all_uids}" ]; then
        echo "Error: no euler-* service users exist yet — nothing to scope the firewall to." >&2
        return 1
    fi

    local proxy_uid acme_uid ddns_uid smtp_uid
    proxy_uid="$(uid_of euler-proxy)"
    acme_uid="$(uid_of euler-acme)"
    ddns_uid="$(uid_of euler-ddns)"
    smtp_uid="$(uid_of euler-smtp)"

    cat <<EOF
#!/usr/sbin/nft -f
# GENERATED by scripts/setup/firewall.sh — kernel egress firewall for the euler
# service tier (DD-8, docs/secure-web-server.md). Regenerate with 'firewall.sh reload'
# after creating a new euler-* user; do not edit by hand.
#
# Scoped uids: $(describe_uids "${ALL_USERS[@]}" "${per_user[@]}")
# Policy accept — non-euler traffic (SSH, root, shells) is never touched.

table inet euler
flush table inet euler

table inet euler {
    chain egress {
        type filter hook output priority filter; policy accept;

        # Replies on established connections (inbound :443 service, allowed egress).
        ct state established,related accept
EOF
    if [ -n "${smtp_uid}" ] && [ -n "${barred_uids}" ]; then
        cat <<EOF

        # Relay guard: of the euler tier, only euler-auth may reach the mail relay.
        ip daddr 127.0.0.0/8 tcp dport ${SMTP_RELAY_PORT} meta skuid { ${barred_uids} } drop
EOF
    fi
    cat <<EOF

        # Loopback is the service fabric: /run/euler sockets, Squid :3128, the relay.
        # Matched by DESTINATION ADDRESS, not 'oif "lo"': the interface-index match
        # does not hit loopback output on the WSL2 kernel (observed on
        # 6.6.114.1-microsoft-standard — euler uids' loopback SYNs fell through to
        # the final drop), and the security intent is the loopback address space.
        ip daddr 127.0.0.0/8 accept
        ip6 daddr ::1 accept
EOF
    if [ -n "${proxy_uid}" ]; then
        cat <<EOF

        # euler-proxy (Squid) — the only real internet path; L7 allowlist on top.
        meta skuid ${proxy_uid} tcp dport { 80, 443 } accept
EOF
    fi
    if [ -n "${acme_uid}" ]; then
        cat <<EOF
        # euler-acme — ACME + DNS-provider API.
        meta skuid ${acme_uid} tcp dport 443 accept
EOF
    fi
    if [ -n "${ddns_uid}" ]; then
        cat <<EOF
        # euler-ddns — name.com API, ipify.
        meta skuid ${ddns_uid} tcp dport 443 accept
EOF
    fi
    if [ -n "${smtp_uid}" ]; then
        cat <<EOF
        # euler-smtp — Gmail submission.
        meta skuid ${smtp_uid} tcp dport 587 accept
EOF
    fi
    if [ -n "${dns_uids}" ]; then
        cat <<EOF

        # DNS for the infra uids (resolvers off-loopback); app tier resolves via lo.
        meta skuid { ${dns_uids} } udp dport 53 accept
        meta skuid { ${dns_uids} } tcp dport 53 accept
EOF
    fi
    cat <<EOF

        # Everything else from the euler tier is dropped.
        meta skuid { ${all_uids} } drop
    }
}
EOF
}

deploy_conf() {
    local tmp
    tmp="$(mktemp)"
    render_conf > "${tmp}"
    echo "Validating the generated ruleset (nft -c)..."
    sudo nft -c -f "${tmp}"
    sudo mkdir -p "${SYS_DIR}"
    sudo install -m 0644 -o root -g root "${tmp}" "${NFT_CONF}"
    rm -f "${tmp}"
    echo "Deployed ${NFT_CONF}"
}

# ── install / uninstall / reload ──────────────────────────────────────────────────

do_install() {
    check_can_sudo || return 1
    require_systemd || return 1
    ensure_deps
    deploy_conf

    echo "Installing ${SERVICE_NAME} (boot-enabled, oneshot)..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler kernel egress firewall (nftables, per-uid — DD-8)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/secure-web-server.md
Wants=network-pre.target
Before=network-pre.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/nft -f ${NFT_CONF}
ExecReload=/usr/sbin/nft -f ${NFT_CONF}
ExecStop=/usr/sbin/nft delete table inet euler

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable --now "${SERVICE_NAME}"
    do_status
}

do_reload() {
    check_can_sudo || return 1
    deploy_conf
    if [ -f "${SERVICE_DEST}" ]; then
        sudo systemctl reload-or-restart "${SERVICE_NAME}"
        echo "Ruleset re-applied."
    else
        echo "note: ${SERVICE_NAME} not installed — run '$0 install' to apply at boot."
    fi
}

do_uninstall() {
    check_can_sudo || return 1
    if [ -f "${SERVICE_DEST}" ]; then
        sudo systemctl disable --now "${SERVICE_NAME}" 2>/dev/null || true
        sudo rm -f "${SERVICE_DEST}"
        sudo systemctl daemon-reload
    fi
    sudo nft delete table inet euler 2>/dev/null || true
    sudo rm -f "${NFT_CONF}"
    echo "Egress firewall uninstall complete (euler table flushed; nothing else touched)."
}

# ── status ────────────────────────────────────────────────────────────────────────

# Probe egress as a given user: expect success (allowed) or failure (dropped).
# Usage: probe <user> <url> <allowed|dropped>
probe() {
    local user="$1" url="$2" expect="$3"
    if ! getent passwd "${user}" > /dev/null; then
        return 0
    fi
    if sudo -u "${user}" curl -sS --max-time 8 -o /dev/null "${url}" 2>/dev/null; then
        if [ "${expect}" = "allowed" ]; then
            echo "  ✓ ${user}: ${url} reachable (allowed)"
        else
            echo "  ✗ ${user}: ${url} reachable — should be DROPPED" >&2
            return 1
        fi
    else
        if [ "${expect}" = "dropped" ]; then
            echo "  ✓ ${user}: ${url} blocked (dropped)"
        else
            echo "  ✗ ${user}: ${url} unreachable — should be allowed" >&2
            return 1
        fi
    fi
}

do_status() {
    local ok=0
    if [ -f "${SERVICE_DEST}" ] && command -v systemctl &> /dev/null; then
        echo "${SERVICE_NAME}: $(systemctl is-active "${SERVICE_NAME}" 2>/dev/null)/$(systemctl is-enabled "${SERVICE_NAME}" 2>/dev/null)"
    else
        echo "${SERVICE_NAME}: ✗ not installed"
    fi
    if command -v nft &> /dev/null && sudo nft list table inet euler &> /dev/null; then
        echo "euler table:  ✓ loaded ($(sudo nft list table inet euler | grep -c 'accept\|drop') rules)"
    else
        echo "euler table:  ✗ not loaded"
        return 1
    fi
    echo "Egress probes (uid-scoped):"
    probe euler-ddns  "https://api.ipify.org" allowed || ok=1
    probe euler-caddy "https://api.ipify.org" dropped || ok=1
    return "${ok}"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    install)   do_install ;;
    uninstall) do_uninstall ;;
    reload)    do_reload ;;
    render)    render_conf ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac
