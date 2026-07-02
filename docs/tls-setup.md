# TLS setup for `solver-web` (Caddy + acme.sh DNS-01, name.com)

> **Status: plan / partially applied.** Caddy is installed (via
> `scripts/setup/caddy.sh`); the cert issuance and Caddy config below are not yet
> done. Authentication for the web front end is a **separate, later** feature —
> see the security note.
>
> **Why acme.sh and not Caddy's own ACME:** the `caddy-dns/namedotcom` plugin is
> unmaintained and no longer builds against current Caddy (the download service
> returns HTTP 400 for it), so Caddy cannot perform the name.com DNS-01 challenge
> itself, and `caddy-dynamicdns` can't drive name.com either. Certificate issuance
> is therefore delegated to **acme.sh**, whose `dns_namecom` client works with the
> name.com API; **stock** Caddy just loads the resulting cert. This keeps the
> DNS-01 benefit (a real cert with no inbound port open) without the broken plugin.

## Goal

Serve the aiohttp front end (`solver/web/app.py`) at
`https://euler.vikasmunshi.com` with a Let's Encrypt certificate that auto-renews.
`solver-web` is unchanged except for its bind address; **Caddy** terminates TLS
and reverse-proxies to aiohttp on loopback, loading a cert that **acme.sh** issues
and renews via the name.com DNS-01 challenge.

## ⚠️ Security phasing — read first

`GET /ws` hands any connected browser a full interactive `solver` shell on a PTY,
and the `POST /<n>/…` routes write files and run commands. That is **arbitrary
remote code execution as this user, with no authentication today.**

TLS provides *encryption*, not *access control*. Enabling TLS does **not** make it
safe to expose this server to the internet. Until the planned authentication
feature lands:

- Complete this setup and **test only from LAN devices.** (DNS-01 needs no inbound
  port, so you can obtain a real cert while staying LAN-only.)
- Do **not** add the router port-forward or the Windows firewall rule (steps 6–7)
  — those are the switches that make the shell publicly reachable — until auth is
  merged.

## Architecture

```
Internet / LAN
   │  https :443
   ▼  Router (FRITZ!Box): forward TCP 443 → 192.168.178.74          [defer until auth exists]
   ▼  Windows Hyper-V Firewall: inbound allow TCP 443               [defer until auth exists]
   ▼  Linux firewall inside WSL: none by default
   ▼
[WSL2]  Caddy  :443  ── terminates TLS ──►  reverse_proxy  ──►  aiohttp 127.0.0.1:8080
             ▲   loads keys/.server.crt + keys/.server.key
             │   reload on renewal
   acme.sh  ─┘   DNS-01 ──► name.com API (writes _acme-challenge TXT)  ──► Let's Encrypt

   DDNS updater ──► name.com API (keeps euler A → current public IP)   [needed only for public access]
```

Port 8080 is bound to loopback and not reachable from the LAN; only :443 is
served. DNS-01 needs no inbound port for the challenge, so nothing on :80.

## The name.com API token

One token drives two things (both outside Caddy):

| Purpose | Record | Driven by | When |
|---|---|---|---|
| **DNS-01 challenge** | `_acme-challenge.euler.vikasmunshi.com` TXT | **acme.sh** (`dns_namecom`) | at issue/renewal; created then deleted |
| **Dynamic DNS** | `euler.vikasmunshi.com` A | **external updater** (see below) | only when public |

## Steps

### 1. name.com API token

name.com account → **API** (api.name.com) → create a token. Note your **username**
and the **token**; keep them secret. They go in the project `.env` (see step 4);
acme.sh caches them for renewals.

### 2. Bind aiohttp to loopback

In `solver/web/cli.py` (`_serve_forever`), change `host='0.0.0.0'` to
`host='127.0.0.1'` so only Caddy on the same host can reach the app.

### 3. Install Caddy (stock)

```bash
scripts/setup/caddy.sh install     # also: update | service | uninstall | status
```

This installs stock Caddy from the official apt repo, **stops/disables the default
`caddy.service`** (bound to the stock Caddyfile) so it does not clash with our
config, and installs our **`caddy-euler.service`** unit (§6) — enabled immediately,
and started automatically once the cert + Caddyfile are in place. No DNS plugin is
needed — acme.sh issues the cert.

### 4. Issue the certificate with acme.sh

Add the name.com credentials to the project `.env` (the same file that holds
`ANTHROPIC_API_KEY`):

```
Namecom_Username=<name.com username>
Namecom_Token=<name.com API token>
```

Then install the acme.sh client and issue + deploy the cert:

```bash
scripts/setup/acme.sh install     # installs acme.sh, default CA = Let's Encrypt
scripts/setup/acme.sh issue       # DNS-01 via dns_namecom → deploy to keys/ → reload Caddy
```

`issue` runs the DNS-01 challenge (no open port needed), writes the full chain to
`keys/.server.crt` and the key to `keys/.server.key` (mode 600; both are dotfiles,
gitignored by `**/.*`), and registers a reload command so Caddy picks up the cert
now and on every renewal. acme.sh's cron auto-renews thereafter
(`scripts/setup/acme.sh renew` forces one).

- The default reload command is `caddy reload --config <root>/Caddyfile` (Caddy's
  admin API, no sudo); override with `EULER_TLS_RELOAD_CMD` if you run Caddy
  differently. Override the domain/email with `EULER_TLS_DOMAIN` / `EULER_TLS_EMAIL`.
- On the very first `issue`, Caddy may not be running yet, so the reload is a
  harmless no-op — the cert still deploys; start Caddy (step 6) and it loads it.

### 5. Caddy configuration

A short Caddyfile — Caddy loads the acme.sh cert (`tls <cert> <key>`) and does **no**
ACME itself. `auto_https disable_redirects` keeps Caddy off :80 (unused with DNS-01):

```caddyfile
{
    auto_https disable_redirects
}

euler.vikasmunshi.com {
    tls keys/.server.crt keys/.server.key
    reverse_proxy 127.0.0.1:8080
}
```

- The cert paths are **relative to Caddy's working directory** — the systemd unit
  (§6) sets `WorkingDirectory` to the repo root, so this file has no machine-specific
  paths. (For a manual `caddy run`, `cd` to the repo root first.)
- `reverse_proxy` upgrades WebSocket connections automatically, so `/ws` works.
- Validate from the repo root: `caddy validate --config Caddyfile`.

### 6. Run Caddy as a service (that can read `keys/`)

acme.sh deploys the cert as the repo owner into `keys/`; the packaged Caddy runs as
the unprivileged `caddy` user, which cannot read files under your home. So Caddy runs
**as the repo owner**. `caddy.sh install` **generates** a `caddy-euler.service` unit
into `/etc/systemd/system/` and enables it — with no hard-coded values: `User`/`Group`
are the checkout's owner, `WorkingDirectory` is the repo root, and the Caddy binary +
config paths are derived, so it's correct on any machine/checkout (`CAP_NET_BIND_SERVICE`
lets it bind :443 without root).

If the cert wasn't present at install time the unit is enabled but not yet started;
start it (once step 4 has issued the cert) with:

```bash
scripts/setup/caddy.sh service     # validates the Caddyfile, then starts the unit
systemctl status caddy-euler
```

- Named `caddy-euler` to avoid colliding with the default `caddy.service` disabled
  in step 3 — do **not** re-enable that default.
- The acme.sh `--reloadcmd` (`caddy reload …`, Caddy's admin API) reloads this
  running instance on every renewal; no sudo needed.

### 7. Router (FRITZ!Box) — defer until auth exists

- Port-forward **TCP 443 → 192.168.178.74** (no port 80 needed for DNS-01).
- Give this machine a **DHCP reservation** (static lease) so `.74` does not drift.

### 8. Windows Hyper-V Firewall — defer until auth exists

Mirrored-mode WSL2 filters inbound traffic via the **Hyper-V Firewall**. From an
**elevated PowerShell on Windows**:

```powershell
New-NetFirewallHyperVRule -Name "WSL-Caddy-443" -DisplayName "WSL Caddy HTTPS" `
  -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' `
  -Protocol TCP -LocalPorts 443 -Action Allow
```

Confirm the VMCreatorId with `Get-NetFirewallHyperVVMCreator`; add specific
per-port rules only. Requires `[wsl2] firewall=true` in `.wslconfig` (default).

## Dynamic DNS (only needed for public access)

The A record must track the ISP's changing public IP for `euler.vikasmunshi.com`
to resolve externally. Caddy's DDNS is unavailable (same broken name.com plugin),
so use one of:

- **Small updater in WSL** (recommended, reuses the name.com token): a script on a
  systemd timer / cron that reads the public IP (`curl https://api.ipify.org`) and
  `PUT`s the name.com A record when it changes.
- **Router (FRITZ!Box) DynDNS** — awkward with name.com's REST API; not recommended.

This is only required once the server is public (post-auth), so wire it up
alongside the router forward.

## Verify

1. `scripts/setup/caddy.sh status` shows Caddy installed and the default service
   inactive/disabled.
2. `acme.sh --issue …` succeeds; `keys/.server.crt` and `keys/.server.key` exist
   (the key mode `0600`).
3. `caddy validate --config Caddyfile` passes; the Caddy service starts and logs
   the loaded certificate (no ACME attempt).
4. From a **LAN device** (with a hosts entry or the resolvable name):
   `curl -v https://euler.vikasmunshi.com/summary` returns the summary page over a
   valid, browser-trusted certificate.
5. Confirm the terminal works: open the site, verify the `/ws` shell connects.
6. Only after authentication exists: add steps 7–8, wire DDNS, and re-test from
   outside the LAN.

## Configuration summary

| Layer | Setting |
|---|---|
| name.com | API token; `_acme-challenge` TXT driven by acme.sh; `euler` A by the DDNS updater |
| acme.sh | issues/renews via `dns_namecom`; deploys cert to `keys/`; reloads Caddy |
| Router (FRITZ!Box) | forward TCP **443** → `192.168.178.74`; static lease |
| Windows Hyper-V Firewall | inbound allow **TCP 443** (`New-NetFirewallHyperVRule`) |
| WSL Linux firewall | none (unless `ufw` is enabled → allow 443) |
| Caddy (WSL) | stock apt build; loads `keys/.server.crt` + `keys/.server.key`; runs as your user |
| aiohttp (WSL) | `solver-web`, bound to `127.0.0.1:8080` |

## Renewal & operation

- **acme.sh** renews the certificate (its cron re-issues before expiry) and runs
  `--reloadcmd` to reload Caddy — no Caddy-side ACME involved.
- **Run a dedicated Caddy service for our Caddyfile, not the packaged default.**
  `scripts/setup/caddy.sh` stops/disables the packaged `caddy.service` (stock
  Caddyfile); supply a separate long-lived unit that runs
  `caddy run --config <path>/Caddyfile` **as your user** (so it can read `keys/`),
  and point acme.sh's `--reloadcmd` at it. Do not re-enable the default service.
- **DDNS** (public only) runs from its own timer/cron.

## Sources

- [acme.sh](https://github.com/acmesh-official/acme.sh) ·
  [dns_namecom API guide](https://github.com/acmesh-official/acme.sh/wiki/dnsapi)
- [Caddy `tls` directive (manual certificates)](https://caddyserver.com/docs/caddyfile/directives/tls)
- [Accessing network applications with WSL — Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [Hyper-V Firewall — Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/hyper-v-firewall)
