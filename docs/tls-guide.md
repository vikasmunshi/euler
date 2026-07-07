# TLS for `solver-web` (Caddy + acme.sh, DNS-01)

> **Partly superseded by the server redesign.** Phase 1 folds the old
> `scripts/setup/caddy.sh` + `scripts/setup/acme.sh` into a single
> `scripts/setup/frontend.sh`, runs the edge as the dedicated `euler-caddy` user, and
> moves the Caddyfile + cert to `/etc/euler` (acme.sh runs as root). The TLS/DNS-01
> mechanics below still apply, but the commands, paths, and service model are current
> only in [`docs/server-redesign.md`](server-redesign.md) (DD-1…DD-3). This guide will
> be rewritten to the new model in a later pass.

This guide covers serving `solver-web` over HTTPS: TLS termination and an
auto-renewing certificate. It is the transport layer of a three-part story —
[authentication](authentication.md) establishes *who* the caller is, and
[authorization](authorization.md) decides *what* they may do.

## What this protects

`GET /ws` hands a browser a full interactive `solver` shell on a PTY, and the
`POST /<n>/…` routes write files and run commands — arbitrary remote code
execution as the repo owner. Three layers guard that surface:

- **TLS** (Caddy, this guide) encrypts the channel and presents a browser-trusted
  certificate. It authenticates nobody — it only secures the transport.
- **[Authentication](authentication.md)** (`solver/web/auth/`) is the access gate,
  in the aiohttp app rather than Caddy, which stays a pure TLS reverse proxy.
- **[Authorization](authorization.md)** (`solver/commands.csv` and the shell)
  decides which commands and routes an authenticated identity may use.

## Architecture

```
Internet / LAN
   │  https :443
   ▼  Router : forward TCP 443 → <host ip> TCP 443
   ▼  System firewall(s): inbound allow TCP 443
   ▼
   Caddy  :443  ── terminates TLS ──►  reverse_proxy  ──►  aiohttp 127.0.0.1:8080
          ▲   loads keys/.server.crt + keys/.server.key                 │  SRP auth gate
          │   reload on renewal                                         │  (solver/web/auth/)
 acme.sh ─┘   DNS-01 ──► Provider API (writes _acme-challenge TXT)  ──► Let's Encrypt

   DDNS updater ──► Provider API (keeps euler A → current public IP)
```

Port 8080 binds to loopback (`solver/web/cli.py` uses `host='127.0.0.1'`) and is
unreachable from the LAN; only Caddy on :443 is exposed. DNS-01 needs no inbound
port for the challenge, so nothing listens on :80.

The aiohttp front end is served at `https://euler.vikasmunshi.com` with an
auto-renewing Let's Encrypt certificate. `solver-web` binds loopback and is
otherwise unchanged; **Caddy** terminates TLS and reverse-proxies to it, loading a
certificate that **acme.sh** issues and renews through a DNS-01 challenge.

**Why acme.sh rather than Caddy's own ACME:** the `caddy-dns/namedotcom` plugin is
unmaintained and no longer builds against current Caddy (its download service
returns HTTP 400), so stock Caddy cannot run the name.com DNS-01 challenge itself.
Issuance is therefore delegated to **acme.sh**, whose `dns_namecom` client speaks
the name.com API, and stock Caddy simply loads the resulting certificate. This
keeps the DNS-01 benefit — a real certificate with no inbound port open — without
depending on a broken plugin.

## The DNS API token

One name.com API token drives two things, both **outside** Caddy:

| Purpose | Record | Driven by | When |
|---|---|---|---|
| **DNS-01 challenge** | `_acme-challenge.euler.vikasmunshi.com` TXT | **acme.sh** (`dns_namecom`) | at issue/renewal; created then deleted |
| **Dynamic DNS** | `euler.vikasmunshi.com` A | **external updater** | only when public |

### 1. Create the token

In the name.com account, open **API** (api.name.com) and create a token. Record
the **username** and the **token**; both go in the project env file `keys/.env` (below), and
acme.sh caches them for renewals.

### 2. Install Caddy (stock)

```bash
scripts/setup/caddy.sh install euler.vikasmunshi.com   # also: update | service | uninstall | status
```

This installs stock Caddy from the official apt repo, **stops and disables the
default `caddy.service`** so it cannot clash, **generates the `Caddyfile`** for the
given hostname, and installs the **`caddy-euler.service`** unit — enabled
immediately and started once the certificate and `Caddyfile` are both in place. No
DNS plugin is required.

Supply the hostname as the `install` argument, via `$EULER_TLS_DOMAIN` (shared with
acme.sh), or at the prompt. The `Caddyfile` is gitignored — it carries the
deployment hostname — and is rewritten on each `install`; a repeated `install` with
no hostname leaves an existing `Caddyfile` untouched.

### 3. Issue the certificate with acme.sh

`acme.sh issue` needs the `Caddyfile` (its reload command points at it), so run
step 2 first. The DNS provider is selectable: pass it to `issue`/`renew`, or set
`$EULER_TLS_DNS_PROVIDER` (default `namecom`). Add the provider's credentials to the
project env file `keys/.env` (the same file that holds `ANTHROPIC_API_KEY`):

| provider (arg) | acme.sh hook | credentials in `keys/.env` |
| --- | --- | --- |
| `namecom` (default) | `dns_namecom` | `NAMEDOTCOM_USERNAME` / `NAMEDOTCOM_TOKEN` |
| `cloudflare` | `dns_cf` | `CF_Token` / `CF_Account_ID` |
| `route53` | `dns_aws` | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` |
| `godaddy` | `dns_gd` | `GD_Key` / `GD_Secret` |
| `digitalocean` | `dns_dgon` | `DO_API_KEY` |
| `gandi` | `dns_gandi_livedns` | `GANDI_LIVEDNS_KEY` |

```bash
scripts/setup/acme.sh install            # installs acme.sh, default CA = Let's Encrypt
scripts/setup/acme.sh issue              # default provider (name.com) DNS-01 → deploy → reload
scripts/setup/acme.sh issue cloudflare   # …or pick another provider
```

`issue` runs the DNS-01 challenge (no open port), writes the full chain to
`keys/.server.crt` and the key to `keys/.server.key` (mode 600; both dot-files,
gitignored by `**/.*`), and registers a reload command so Caddy picks up the
certificate immediately and on every renewal. acme.sh's cron then auto-renews
(`scripts/setup/acme.sh renew [provider]` forces a renewal).

- The default reload command is `caddy reload --config <root>/Caddyfile` (Caddy's
  admin API, no sudo); override it with `EULER_TLS_RELOAD_CMD`. Override the
  domain/email with `EULER_TLS_DOMAIN` / `EULER_TLS_EMAIL`.
- On the very first `issue`, Caddy may not be running yet, so the reload is a
  harmless no-op — the certificate still deploys; start Caddy (§4) and it loads it.

### 4. The Caddyfile & service

`caddy.sh install` **generates** this `Caddyfile` for the hostname (gitignored, not
tracked). Caddy loads the acme.sh certificate and performs no ACME of its own;
`auto_https disable_redirects` keeps it off :80:

```caddyfile
{
    auto_https disable_redirects
}

euler.vikasmunshi.com {
    tls keys/.server.crt keys/.server.key
    reverse_proxy 127.0.0.1:8080
}
```

- Certificate paths are **relative to Caddy's working directory** — the systemd
  unit sets `WorkingDirectory` to the repo root, so the file carries no
  machine-specific paths. (For a manual `caddy run`, `cd` to the repo root first.)
- `reverse_proxy` upgrades WebSocket connections automatically, so `/ws` works.
- Validate from the repo root: `caddy validate --config Caddyfile`.

acme.sh deploys the certificate into `keys/` as the repo owner, and the packaged
Caddy runs as the unprivileged `caddy` user, which cannot read files under the
owner's home. The generated **`caddy-euler.service`** therefore runs Caddy **as the
repo owner**: `User`/`Group` are the checkout's owner, `WorkingDirectory` is the
repo root, and the binary and config paths are derived (`CAP_NET_BIND_SERVICE` lets
it bind :443 without root). If the certificate is absent at install time, the unit
is enabled but not started; start it once §3 has issued one:

```bash
scripts/setup/caddy.sh service     # validates the Caddyfile, then starts the unit
systemctl status caddy-euler
```

The unit is named `caddy-euler` to avoid colliding with the default
`caddy.service`; do **not** re-enable that default. acme.sh's `--reloadcmd` reloads
the running instance on every renewal.

## Going public (router + firewall)

These steps expose the server beyond the LAN. They are needed only for public
access; [authentication](authentication.md) and [authorization](authorization.md)
are what make that access safe.

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

The A record must track the ISP's changing public IP. Caddy's DDNS relies on the
same broken name.com plugin, so drive it separately with a **small updater in WSL**
on a systemd timer or cron: read the public IP (`curl https://api.ipify.org`) and
`PUT` the name.com A record when it changes. (Router DynDNS is awkward against
name.com's REST API and is not recommended.)

## Configuration summary

`keys/.env` keys for TLS: `NAMEDOTCOM_USERNAME` / `NAMEDOTCOM_TOKEN` (or the chosen DNS
provider's pair). The certificate files (`keys/.server.crt`, `keys/.server.key`) are
dot-files, gitignored by `**/.*`.

| Layer | Setting |
|---|---|
| DNS provider | API token; `_acme-challenge` TXT via acme.sh; the `euler` A record via the DDNS updater (public only) |
| acme.sh | issues/renews via the provider's DNS-01 hook; deploys the cert to `keys/`; reloads Caddy |
| Caddy | stock apt build; loads `keys/.server.crt` + `keys/.server.key`; runs as the repo owner |
| aiohttp | `solver-web`, bound to `127.0.0.1:8080`; SRP auth gate in `solver/web/auth/` |
| Router | forward TCP 443 → the host's LAN IP; static lease (public only) |
| System firewall | inbound allow TCP 443 (public only) |

## Verify

1. `scripts/setup/caddy.sh status` shows Caddy installed and the default service
   inactive/disabled.
2. `keys/.server.crt` and `keys/.server.key` exist (key mode `0600`);
   `caddy validate --config Caddyfile` passes and the service logs the loaded
   certificate with no ACME attempt.
3. From a LAN device, `curl -v https://euler.vikasmunshi.com/login` returns the login
   page over a valid, browser-trusted certificate.
4. For public access, add the router forward and firewall rule, wire up DDNS, and
   re-test from outside the LAN. (Do this only once authentication is in place — see
   [authentication](authentication.md).)

## Renewal & operation

- **acme.sh** renews the certificate (its cron re-issues before expiry) and runs
  `--reloadcmd` to reload Caddy; no Caddy-side ACME is involved.
- Run the dedicated **`caddy-euler.service`**, not the packaged default; it runs as
  the repo owner so it can read `keys/`. Do not re-enable the default
  `caddy.service`.
- The **DDNS** updater (public access only) runs from its own timer or cron.

## Sources

- [acme.sh](https://github.com/acmesh-official/acme.sh) ·
  [dnsapi guide](https://github.com/acmesh-official/acme.sh/wiki/dnsapi)
- [Caddy `tls` directive (manual certificates)](https://caddyserver.com/docs/caddyfile/directives/tls)
- [Accessing network applications with WSL — Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [Hyper-V Firewall — Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/hyper-v-firewall)
