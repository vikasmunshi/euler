#!/usr/bin/env bash
# Kernel egress firewall kit (nftables): per-uid rules for where each service may connect.
# ========================================================================================
#
# Deploys / removes the host nftables ruleset that makes "egress only via Squid"
# a *kernel* property instead of an environment-variable convention: scoped to the
# euler-* service uids, it permits only the specific (uid, port) egress each service
# genuinely needs — on loopback as much as off-host — then drops the rest. Sibling to frontend.sh /
# egress.sh / ddns.sh / smtp.sh; see docs/web-server-guide.md § Egress.
#
# Model:
#   - A dedicated `table inet euler` with one egress-only (hook output) chain,
#     policy accept: non-service traffic — SSH, root, your shell — is untouched
#     (no lock-out risk); only the enumerated euler-* uids hit the final drop.
#   - ct state established/related is accepted first, so euler-caddy can answer
#     inbound public connections on :443 while still being unable to *initiate*
#     anything off-host (its NEW outbound is dropped).
#   - Loopback is an allowlist too: the services talk over unix sockets, so the only
#     loopback TCP the tier needs is Squid :3128, DNS :53 and — for euler-auth alone —
#     the mail relay. Anything else listening on 127.0.0.1 (Caddy's admin API before it
#     moved to a socket, an IDE, sshd) is out of reach of a hostile per-user web shell.
#   - The ruleset is generated with *numeric* uids resolved at generation time and
#     includes only the euler-* users that exist; rerun `reload` (or the installing
#     kit runs it) after a new service user lands.
#   - This is egress layer 2; layer 1 (per-unit IPAddressDeny=any +
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
#   all euler-*   loopback 3128 — Squid; and loopback 53 — the local resolver
#   euler-auth    loopback 8025 — the mail relay (its only client)
#
# Actions: deploy | remove | reload | render | status | help
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

# ── The euler service tier ───────────────────────────────────────
# Every euler-* uid subject to the egress drop. Generated rules include only the
# users that exist at generation time. The web app tier runs as per-user uids
# (one uid per collaborator), resolved dynamically by group (see euler_user_names);
# only the fixed infra uids are listed statically here.
ALL_USERS=(euler-caddy euler-auth euler-msg euler-site
           euler-proxy euler-acme euler-ddns euler-smtp)
# Infra uids allowed direct DNS (the app tier resolves via loopback only).
DNS_USERS=(euler-proxy euler-acme euler-ddns euler-smtp)
# The mail relay's one client. Every other uid — the per-user web shells (RCE by design,
# AR-1) above all — is left to the final drop. euler-msg sends no e-mail, which is what
# lets its unit run AF_UNIX-only (docs/web-server-guide.md § Messaging — No mail).
RELAY_CLIENT="euler-auth"
# Squid's loopback port (must match egress.sh): the one loopback TCP port the app tier needs.
PROXY_PORT="3128"

usage() {
    cat <<USAGE
Usage: $0 [deploy|remove|reload|render|status|help]

  deploy     Install nftables, generate ${NFT_CONF} and install the root-owned,
             boot-enabled ${SERVICE_NAME} (oneshot: loads the euler table).
             Idempotent — it is also its own upgrade path.
  remove     Flush the euler table and remove the ruleset + unit.
  reload     Regenerate the ruleset (picking up newly created euler-* and per-user uids) and
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

# The per-user web tier creates its uids dynamically at provision time, so they cannot be
# listed ahead of time like the fixed service uids. They are named for the collaborator's
# system slug alone (ue0f4a1 — no euler- prefix), so the enumerable set is the euler-user
# PARENT GROUP every provisioned uid joins (user.sh), not a name pattern. A reload after
# each provision folds the new uid into the egress drop (chain policy is accept — an
# unlisted uid would reach the internet directly, bypassing Squid). They are
# RCE-by-design (AR-1), so they get no loopback port beyond Squid and DNS.
USER_GROUP="euler-user"
euler_user_names() {
    getent group "${USER_GROUP}" 2>/dev/null | awk -F: '{print $4}' | tr ',' '\n' | sed '/^$/d'
}

# Generate the ruleset to stdout. Uses the declare-then-flush pattern so re-applying
# with `nft -f` is idempotent.
render_conf() {
    local all_uids dns_uids per_user
    # Read the dynamic per-user uids (the euler-user group) once; they join the egress drop
    # alongside the fixed service uids.
    mapfile -t per_user < <(euler_user_names)
    all_uids="$(resolve_uids "${ALL_USERS[@]}" "${per_user[@]}")"
    dns_uids="$(resolve_uids "${DNS_USERS[@]}")"
    if [ -z "${all_uids}" ]; then
        echo "Error: no euler-* service users exist yet — nothing to scope the firewall to." >&2
        return 1
    fi

    local proxy_uid acme_uid ddns_uid smtp_uid relay_uid
    proxy_uid="$(uid_of euler-proxy)"
    relay_uid="$(uid_of "${RELAY_CLIENT}")"
    acme_uid="$(uid_of euler-acme)"
    ddns_uid="$(uid_of euler-ddns)"
    smtp_uid="$(uid_of euler-smtp)"

    cat <<EOF
#!/usr/sbin/nft -f
# GENERATED by scripts/setup/firewall.sh — kernel egress firewall for the euler
# service tier (docs/web-server-guide.md § Egress). Regenerate with 'firewall.sh reload'
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
    cat <<EOF

        # Loopback is an allowlist, not the service fabric: the services talk over unix
        # sockets, so only these loopback ports are open to the euler tier — Squid and the
        # local resolver for every uid, the mail relay for its one client. Anything else
        # on 127.0.0.1 (an IDE, sshd, an admin API) falls through to the final drop.
        # Matched by DESTINATION ADDRESS, not 'oif "lo"': the interface-index match
        # does not hit loopback output on the WSL2 kernel (observed on
        # 6.6.114.1-microsoft-standard — euler uids' loopback SYNs fell through to
        # the final drop), and the security intent is the loopback address space.
        ip daddr 127.0.0.0/8 tcp dport ${PROXY_PORT} accept
        ip6 daddr ::1 tcp dport ${PROXY_PORT} accept
        ip daddr 127.0.0.0/8 meta l4proto { tcp, udp } th dport 53 accept
        ip6 daddr ::1 meta l4proto { tcp, udp } th dport 53 accept
EOF
    if [ -n "${smtp_uid}" ] && [ -n "${relay_uid}" ]; then
        cat <<EOF
        meta skuid ${relay_uid} ip daddr 127.0.0.0/8 tcp dport ${SMTP_RELAY_PORT} accept
EOF
    fi
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

        # DNS for the infra uids (resolvers off-loopback); app tier resolves via lo (above).
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

do_deploy() {
    check_can_sudo || return 1
    require_systemd || return 1
    ensure_deps
    deploy_conf

    echo "Installing ${SERVICE_NAME} (boot-enabled, oneshot)..."
    sudo tee "${SERVICE_DEST}" > /dev/null <<EOF
[Unit]
Description=euler kernel egress firewall (nftables, per-uid)
Documentation=https://github.com/vikasmunshi/euler/blob/master/docs/web-server-guide.md
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
        echo "note: ${SERVICE_NAME} not installed — run '$0 deploy' to apply at boot."
    fi
}

do_remove() {
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

# Probe a loopback TCP port as a given user, by connect() alone (the port need not speak
# HTTP): a drop hangs until the timeout, a refusal fails at once (nothing listening — no
# verdict), a connect means allowed. Usage: probe_tcp <user> <port> <allowed|dropped>
probe_tcp() {
    local user="$1" port="$2" expect="$3" rc
    getent passwd "${user}" > /dev/null || return 0
    sudo -u "${user}" timeout 3 bash -c "exec 3<>/dev/tcp/127.0.0.1/${port}" 2>/dev/null
    rc=$?
    case "${rc}:${expect}" in
        0:allowed)   echo "  ✓ ${user}: 127.0.0.1:${port} reachable (allowed)" ;;
        124:dropped) echo "  ✓ ${user}: 127.0.0.1:${port} blocked (dropped)" ;;
        0:dropped)   echo "  ✗ ${user}: 127.0.0.1:${port} reachable — should be DROPPED" >&2; return 1 ;;
        124:allowed) echo "  ✗ ${user}: 127.0.0.1:${port} dropped — should be allowed" >&2; return 1 ;;
        *)           echo "  … ${user}: 127.0.0.1:${port} refused (nothing listening — no verdict)" ;;
    esac
}

do_status() {
    local ok=0 tenant
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
    # Loopback: a per-user web shell reaches Squid and nothing else (the relay listens, so it
    # proves the drop); euler-auth still reaches the relay.
    tenant="$(euler_user_names | head -1)"
    if [ -n "${tenant}" ]; then
        probe_tcp "${tenant}"  "${PROXY_PORT}"      allowed || ok=1
        probe_tcp "${tenant}"  "${SMTP_RELAY_PORT}" dropped || ok=1
    fi
    probe_tcp "${RELAY_CLIENT}" "${SMTP_RELAY_PORT}" allowed || ok=1
    return "${ok}"
}

# ── Dispatch ──────────────────────────────────────────────────────────────────────
ACTION="${1:-status}"
case "${ACTION}" in
    deploy)    do_deploy ;;
    remove)    do_remove ;;
    reload)    do_reload ;;
    render)    render_conf ;;
    status)    do_status ;;
    -h | --help | help) usage ;;
    *) echo "Unknown action: ${ACTION}"; usage; exit 1 ;;
esac
