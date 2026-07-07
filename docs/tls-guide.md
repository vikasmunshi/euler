# TLS for the web edge (Caddy + acme.sh, DNS-01)

This guide covers the **edge**: TLS termination on `:443` and an auto-renewing
certificate, as built by `scripts/setup/frontend.sh` (Phase 1 of the
[server redesign](server-redesign.md)). It is the transport layer of a three-part
story — [authentication](authentication.md) establishes *who* the caller is, and
[authorization](authorization.md) decides *what* they may do.

The edge runs as the dedicated **`euler-caddy`** user, and its config + certificate
live under **`/etc/euler`** (decoupled from the repo). See the design of record —
[`server-redesign.md`](server-redesign.md) — for the full service topology and the
locked decisions DD-1 (unix-socket transport), DD-2 (service users), and DD-3
(`frontend.sh` + root-owned systemd).

## What this protects

The web front end exposes a PTY-backed `solver` shell (over a WebSocket) and file
write / command routes — arbitrary remote code execution by design. Three
independent layers guard that surface:

- **TLS** (Caddy, this guide) encrypts the channel and presents a browser-trusted
  certificate. It authenticates nobody — it only secures the transport — and adds
  the transport-level security headers (HSTS, `X-Content-Type-Options`,
  `Referrer-Policy`) plus a fallback CSP.
- **[Authentication](authentication.md)** is the access gate: Caddy routes every
  request through the auth service's `forward_auth` endpoint before it reaches
  content or the shell, so those services never see an unauthenticated caller.
- **[Authorization](authorization.md)** (`solver/commands.csv` and the shell)
  decides which commands and routes an authenticated identity may use.

> **Build status.** Phase 1 (this guide) delivers the edge: TLS, the cert, security
> headers, a Caddy-native `/healthz`, and a maintenance placeholder. The
> `forward_auth` gate and the `unix//run/euler/*` upstreams below are shipped as
> commented stubs in the generated Caddyfile and activated by later phases (auth =
> Phase 4, content = Phase 5, shell WS = Phase 6).

## Architecture

```
Internet / LAN
   │  https :443
   ▼  Router: forward TCP 443 → <host LAN ip>:443   ·   Firewall: inbound allow 443
   ▼
   Caddy :443   ── runs as euler-caddy, config /etc/euler/Caddyfile ──
      │  terminates TLS (loads /etc/euler/tls/server.{crt,key})
      │  security headers + fallback CSP; forward_auth gate
      ├─►  unix //run/euler/auth.sock       (euler-auth)      — Phase 4
      ├─►  unix //run/euler/content.sock    (euler-content)   — Phase 5
      └─►  unix //run/euler/ws.sock         (euler-ws)        — Phase 6
   ▲
 acme.sh (root, /root/.acme.sh)
   └─  DNS-01 ─► name.com API (writes _acme-challenge TXT) ─► Let's Encrypt
       reloadcmd: re-apply cert perms + `systemctl reload euler-caddy.service`

 DDNS updater ─► name.com API (keeps the euler A record → current public IP)
```

No app service binds a TCP port — Caddy reaches each one over a **unix domain socket**
under `/run/euler` (DD-1), and only Caddy on `:443` is network-exposed. DNS-01 needs no
inbound port for the challenge, so nothing listens on `:80`
(`auto_https disable_redirects`).

**Why acme.sh rather than Caddy's own ACME:** the `caddy-dns/namedotcom` plugin is
unmaintained and no longer builds against current Caddy, so stock Caddy cannot run the
name.com DNS-01 challenge itself. Issuance is delegated to **acme.sh** (whose
`dns_namecom` client speaks the name.com API); stock Caddy simply loads the resulting
certificate. This keeps the DNS-01 benefit — a real certificate with no inbound port
open — without a broken plugin.

## The DNS API token

One name.com API token drives two things, both **outside** Caddy:

| Purpose | Record | Driven by | When |
|---|---|---|---|
| **DNS-01 challenge** | `_acme-challenge.euler.vikasmunshi.com` TXT | **acme.sh** (`dns_namecom`) | at issue/renewal; created then deleted |
| **Dynamic DNS** | `euler.vikasmunshi.com` A | **`scripts/setup/ddns.sh`** (host timer) | only when public |

Create a token in the name.com account (**API**, api.name.com) and record the
**username** and the **token**; both go in the project env file `keys/.env` (below), and
acme.sh caches them for renewals.

## Install the edge

Set the deployment FQDN once in `keys/.env` (the **single source of truth**, shared with
`ddns.sh`), then one command stands up the whole edge — group + user, Caddy, acme.sh, the
Caddyfile, the certificate, and the systemd unit:

```bash
echo 'EULER_TLS_DOMAIN=euler.vikasmunshi.com' >> keys/.env   # if not already set
scripts/setup/frontend.sh install
# also: uninstall | upgrade | status | renew | reload
```

`frontend.sh` reads the FQDN from `keys/.env` (`EULER_TLS_DOMAIN`) and **fails if it is
unset** — there is no hostname argument or prompt. `install` is idempotent and does, in
order:

1. creates the **`euler-web`** group and the **`euler-caddy`** system user (DD-2);
2. installs stock Caddy from the official apt repo and **disables** any conflicting
   unit (the stock `caddy.service` and the old `caddy-euler.service`);
3. generates **`/etc/euler/Caddyfile`** for the FQDN (§ below);
4. installs **acme.sh as root** (`/root/.acme.sh`, with a root renewal cron);
5. issues the certificate via DNS-01 and deploys it to **`/etc/euler/tls`**;
6. installs the root-owned, boot-enabled **`euler-caddy.service`** and starts it.

### DNS credentials

The DNS provider is selectable via `$EULER_TLS_DNS_PROVIDER` (default `namecom`); add
its credentials to `keys/.env` (the same file that holds `ANTHROPIC_API_KEY`):

| provider | acme.sh hook | credentials in `keys/.env` |
| --- | --- | --- |
| `namecom` (default) | `dns_namecom` | `NAMEDOTCOM_USERNAME` / `NAMEDOTCOM_TOKEN` (or `Namecom_Username` / `Namecom_Token`) |
| `cloudflare` | `dns_cf` | `CF_Token` / `CF_Account_ID` |
| `route53` | `dns_aws` | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` |
| `godaddy` | `dns_gd` | `GD_Key` / `GD_Secret` |
| `digitalocean` | `dns_dgon` | `DO_API_KEY` |
| `gandi` | `dns_gandi_livedns` | `GANDI_LIVEDNS_KEY` |

`frontend.sh` reads `keys/.env` as the invoking user and passes the credentials to the
root acme.sh **as environment** (acme.sh caches them under `/root/.acme.sh` for
unattended renewals). acme.sh refuses to run under a bare `sudo`, so the script invokes
it as *clean* root (stripping the `SUDO_*` markers) — no manual step needed.

## The Caddyfile

`frontend.sh` **generates** `/etc/euler/Caddyfile` (`root:euler-web`, mode `0640`, so
`euler-caddy` can read it). Caddy loads the acme.sh certificate by **absolute path** and
performs no ACME of its own:

```caddyfile
{
    # DNS-01 needs no inbound :80, so keep Caddy off :80 (no HTTP->HTTPS redirect).
    auto_https disable_redirects
}

euler.vikasmunshi.com {
    tls /etc/euler/tls/server.crt /etc/euler/tls/server.key

    # Transport-level security headers; the per-response nonce'd CSP is minted by the
    # app tier in later phases — this is the static/edge fallback.
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

    # --- Later phases (shipped as commented stubs) ---
    #   forward_auth unix//run/euler/auth.sock { uri /verify; copy_headers X-User }
    #   handle_path /ws* { reverse_proxy unix//run/euler/ws.sock }     # Phase 6
    #   handle          { reverse_proxy unix//run/euler/content.sock }  # Phase 5

    # Until app services exist, everything else is the maintenance holding page.
    handle {
        respond "euler - under maintenance" 200
    }
}
```

- `reverse_proxy` upgrades WebSocket connections automatically, so `/ws` will work once
  the Phase-6 upstream is uncommented.
- Regenerate + validate: `scripts/setup/frontend.sh upgrade` rewrites the Caddyfile and
  reloads the unit; `sudo caddy validate --config /etc/euler/Caddyfile` checks it.

## The service

The generated **`euler-caddy.service`** is a **root-owned** system unit
(`/etc/systemd/system`), enabled at boot, that runs Caddy as the unprivileged
`euler-caddy` user:

- `User=euler-caddy`, `Group=euler-web`, `WorkingDirectory=/etc/euler`.
- `AmbientCapabilities=CAP_NET_BIND_SERVICE` lets it bind `:443` without root.
- `RuntimeDirectory=euler` provisions `/run/euler` (mode `0770`) for the app-service
  sockets; `StateDirectory=euler-caddy` + `XDG_*` give Caddy a writable home.
- Hardening: `NoNewPrivileges`, `ProtectHome`, `ProtectSystem=full`, `PrivateTmp`.

Because the unit lives in **root's** systemd and runs as a locked-down user, lifecycle
is privileged — **start/stop/restart need `sudo`** (DD-3):

```bash
sudo systemctl status euler-caddy         # or: scripts/setup/frontend.sh status
sudo systemctl restart euler-caddy
scripts/setup/frontend.sh reload          # sudo systemctl reload euler-caddy
```

`euler-caddy.service` supersedes the old repo-owner `caddy-euler.service` (which
`frontend.sh` removes); do **not** re-enable the stock `caddy.service`.

### Why /etc/euler (not the repo)

`euler-caddy` cannot traverse the repo owner's `0750` home directory, so a repo-local
Caddyfile or key would be unreadable. `frontend.sh` therefore writes the Caddyfile to
`/etc/euler/Caddyfile` and the certificate to `/etc/euler/tls`, fully decoupling the
edge from the checkout (DD-3). Cert perms: `server.crt` `0644`, `server.key` `0640`,
both `root:euler-web` — readable by `euler-caddy` via the group.

## Going public (router + firewall)

These steps expose the server beyond the LAN. They are needed only for public access;
[authentication](authentication.md) and [authorization](authorization.md) are what make
that access safe.

### Router

- Port-forward **TCP 443 → the host's LAN IP** (no port 80 needed for DNS-01).
- Give the host a **DHCP reservation** so its LAN IP does not drift.

### System firewall (Windows Hyper-V Firewall)

On mirrored-mode WSL2, inbound traffic is filtered by the Windows Hyper-V Firewall.
From an **elevated PowerShell on Windows**:

```powershell
New-NetFirewallHyperVRule -Name "WSL-Caddy-443" -DisplayName "WSL Caddy HTTPS" `
  -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' `
  -Protocol TCP -LocalPorts 443 -Action Allow
```

Confirm the VMCreatorId with `Get-NetFirewallHyperVVMCreator`, and add specific
per-port rules only. Requires `[wsl2] firewall=true` in `.wslconfig` (the default).

### Dynamic DNS

The A record must track the ISP's changing public IP. `scripts/setup/ddns.sh` does this
from the host — no external service:

```bash
scripts/setup/ddns.sh install    # installs euler-ddns.timer (root, every 5 min)
scripts/setup/ddns.sh update     # update the A record now
scripts/setup/ddns.sh status     # timer state, public IP, live A record
```

It reads the public IP (`api.ipify.org`) and PUTs the name.com A record via the v4 API
only when it has changed, using the **same name.com token as the DNS-01 challenge**
(`keys/.env`). `euler-ddns.timer` runs it as **root** (like the acme.sh renewal cron),
so — being infra egress — it does **not** pass through the Squid proxy.

## Renewal & operation

- **acme.sh** (root cron) renews the certificate before expiry and runs its
  `--reloadcmd`, which **re-applies the `root:euler-web` ownership/mode** (that
  `--install-cert` resets) and then `systemctl reload euler-caddy.service`. No
  Caddy-side ACME is involved.
- **Renewal needs no DNS credentials re-supplied.** acme.sh saves the name.com token
  in the certificate's `.conf` at issue time (`SAVED_Namecom_*`) and re-exports it for
  the DNS-01 challenge on renewal — which is exactly what lets the unattended root cron
  work. `frontend.sh renew` therefore does *not* load `keys/.env`.
- Force a renewal with `scripts/setup/frontend.sh renew`; check the schedule with
  `frontend.sh status` (the `Renewal:` line shows the root cron + next renewal).
- The **DDNS** updater (public access only) runs from `euler-ddns.timer`
  (`scripts/setup/ddns.sh`).

## Configuration summary

`keys/.env` keys for the edge: **`EULER_TLS_DOMAIN`** (the FQDN — single source of truth,
shared by `frontend.sh` and `ddns.sh`) and the chosen DNS provider's credential pair
(default `NAMEDOTCOM_USERNAME` / `NAMEDOTCOM_TOKEN`).

| Layer | Setting |
|---|---|
| DNS provider | API token; `_acme-challenge` TXT via acme.sh; the `euler` A record via the DDNS updater (public only) |
| acme.sh | root install (`/root/.acme.sh`); issues/renews via the DNS-01 hook; deploys to `/etc/euler/tls`; reload hook fixes perms + reloads the unit |
| Caddy | stock apt build; runs as `euler-caddy`; loads `/etc/euler/tls/server.{crt,key}`; config `/etc/euler/Caddyfile` |
| Upstreams | `unix//run/euler/*` sockets behind `forward_auth` (later phases) |
| Router | forward TCP 443 → the host's LAN IP; static lease (public only) |
| System firewall | inbound allow TCP 443 (public only) |

## Verify

1. `scripts/setup/frontend.sh status` shows Caddy + acme.sh installed, the cert expiry,
   `euler-caddy.service` `active/enabled`, and `/healthz → HTTP 200`.
2. `/etc/euler/tls/server.crt` and `server.key` exist (`root:euler-web`, key `0640`);
   `sudo caddy validate --config /etc/euler/Caddyfile` passes and the service logs the
   loaded certificate with no ACME attempt.
3. From a LAN device, `curl -v https://euler.vikasmunshi.com/healthz` returns `ok` over a
   valid, browser-trusted certificate.
4. For public access, add the router forward and firewall rule, wire up DDNS, and re-test
   from outside the LAN. (Do this only once authentication is in place — see
   [authentication](authentication.md).)

## Sources

- [acme.sh](https://github.com/acmesh-official/acme.sh) ·
  [dnsapi guide](https://github.com/acmesh-official/acme.sh/wiki/dnsapi) ·
  [running under sudo](https://github.com/acmesh-official/acme.sh/wiki/sudo)
- [Caddy `tls` directive (manual certificates)](https://caddyserver.com/docs/caddyfile/directives/tls)
- [Accessing network applications with WSL — Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [Hyper-V Firewall — Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/hyper-v-firewall)
