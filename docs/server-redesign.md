# `solver-web` server redesign

A ground-up rebuild of the web front end as a set of **isolated services** behind a
single edge, delivering **server-rendered pages that feel live** (no
skeleton-page + client-fetch architecture). This is the design of record for that
rebuild; it is the transport/app-layer companion to [tls-guide.md](tls-guide.md),
[authentication.md](authentication.md), and [authorization.md](authorization.md).

> **Status (2026-07-07).** Built feature-by-feature (see [Phases](#phases)); each phase
> ships its full [maintenance kit](#the-maintenance-kit-per-feature-contract) before the
> next begins.
> - ✅ **Phase 1** — Caddy + ACME edge (TLS, renewal, health endpoint).
> - ✅ **Phase 2** — Squid egress (allowlist, `euler-proxy`).
> - ✅ **Phase 3** — static maintenance holding page (503 fallback + CSP).
> - 🔨 **Phase 4** — Auth service: decisions locked ([DD-5](#design-decisions)…[DD-9](#design-decisions)); **in progress** — build-order step 1 (firewall + smtp kits) ✅, steps 2–5 pending (see [Phase 4](#phase-4--auth-service)).
> - ⬜ **Phases 5–6** — content service, web shell (not started).

## Goals & non-goals

**Goals**
- Every page is **composed server-side** from shared templates; the browser never
  assembles content from JSON. One template set renders both full pages and the
  fragments that update them.
- **Feels live** without a client framework or a build toolchain: request-driven
  fragment swaps + server-pushed updates for long-running work.
- **Service isolation**: edge, egress, auth, content, and shell are separate
  processes with separate blast radii, wired only over loopback / unix sockets.
- **Server-side security validation** on every write path; a strict
  **Content-Security-Policy on every served page**.
- Each feature arrives with a complete **maintenance kit** — install/uninstall/
  update, config generation, and start/stop/status — so the system is operable at
  every step, not only when finished.

**Non-goals**
- No SPA / client-side router / client-side templating. "HTML5 app feel" is met by
  server-rendered fragment swaps, not by moving rendering to the client.
- No second language runtime. Everything stays Python + vendored browser assets;
  the PTY shell (the hardest existing code) is reused, not rewritten.
- No offline/PWA service worker in scope (revisit only if an explicit offline
  requirement appears).

## Locked decisions

| Concern | Decision |
|---|---|
| TLS / edge / routing | **Caddy** (reverse proxy, `forward_auth` gate), certs via **acme.sh** DNS-01. |
| Inter-service transport | **Unix domain sockets** under `/run/euler/`, not loopback TCP — see [DD-1](#design-decisions). |
| Service identity | Dedicated nologin system users — `euler-caddy` / `euler-auth` / `euler-content` / `euler-ws` (in **`euler-web`**), plus `euler-proxy` (egress), `euler-acme` (cert), `euler-ddns` (DNS), `euler-smtp` (mail relay). **None run as root** — see [DD-2](#design-decisions), [DD-4](#design-decisions). |
| Edge setup & lifecycle | One `scripts/setup/frontend.sh` (install/uninstall/upgrade) installs **root-owned systemd units** (start/stop needs `sudo`), superseding `caddy.sh` + `acme.sh` — see [DD-3](#design-decisions). |
| Egress control | **Squid** forward proxy, domain allowlist; shell/AI/scrapers reach the network only via `HTTPS_PROXY`. |
| Response headers | **Content-Security-Policy on every served page** (see [CSP](#content-security-policy)). |
| App framework / templating | **aiohttp + Jinja2** (autoescape on) across the app services — see [DD-5](#design-decisions), [Framework/templating](#framework--templating). |
| App runtime | Deployed to a **root-owned `/opt/euler` system venv** (`pip install .`); services run `/opt/euler/venv/bin/python -m …`. Repo stays unreadable to service users — see [DD-5](#design-decisions). |
| Auth state & admin plane | Auth state in **`/var/lib/euler-auth`** (`euler-auth`-only, `0600`); admin ops (`users add/list/disable`) go through an **admin API on the auth socket**, never file-sharing — see [DD-6](#design-decisions). |
| Registration | **Invite-only**, two-channel: admin-minted **7-day** email link → Terms acceptance → **10-min OTP** → set SRP password — see [DD-7](#design-decisions). |
| Egress firewall | **Kernel-enforced**: systemd per-unit `IPAddressDeny` (loopback-only app tier) + host **nftables** owner-match; mail via a loopback `euler-smtp` relay — see [DD-8](#design-decisions). |
| Identity & masquerade | Three planes — web requests (`forward_auth` → `X-User`/`X-Profile`), web shells (**one-time shell ticket** redeemed over `auth.sock`), local terminal (**checkout-owner uid** → admin). Fresh **`solver/web/auth`** package; the `keys/` web-auth store is **not ported** — see [DD-9](#design-decisions). |

## Open decisions (this document argues, you choose)

- ~~**Framework/templating**~~ → **resolved: aiohttp + Jinja2** ([DD-5](#design-decisions)).
- **htmx**: adopt for liveness? → [benefits vs consequences](#htmx).
- **nh3**: adopt for HTML sanitisation? → [benefits vs consequences](#nh3).

---

## Target topology

```
                          :443
  browser ───TLS──▶  ┌──────────┐
                     │  Caddy    │  edge: TLS, routing by path, security headers
                     │  (edge)   │  forward_auth ─────────────┐
                     └────┬──────┘                            │
            unix sockets /run/euler                           ▼
        ┌───────────┬─────────────┬──────────────┐     ┌────────────┐
        ▼           ▼             ▼               ▼     │   auth      │  SRP login,
   ┌─────────┐ ┌──────────┐ ┌───────────┐              │  service    │  sessions,
   │ maint.  │ │ content   │ │  ws /      │◀────────────│ (aiohttp)   │  forward_auth
   │ (static)│ │ (aiohttp  │ │  shell     │             └────────────┘  → 200 + X-User
   └─────────┘ │ + Jinja2) │ │ (aiohttp   │                              or 401
               └────┬──────┘ │  + PTY)    │
                    │        └─────┬──────┘
      reads solution tree          │ spawns `python -m solver`
      (plaintext, incl.            │
       solutions/private)          ▼
                              ┌──────────┐   allowlist egress only
        all outbound ────────▶│  Squid    │──▶ api.anthropic.com,
        (AI, scraper, gh)     │ (egress)  │    projecteuler.net, github
                              └──────────┘
```

Every app service binds a **unix domain socket** under `/run/euler/` (see the
[Design decisions](#design-decisions)); **only Caddy is publicly bound**. Caddy
authenticates every request through the auth service's `forward_auth` endpoint before
it reaches content or shell, so those services never see an unauthenticated caller
even if they have a bug.

---

## Design decisions

Locked, ADR-style. These fix the Phase-1 choices the rest of the doc left implicit;
each is summarised in the [Locked decisions](#locked-decisions) table.

### DD-1 · Inter-service transport = unix domain sockets

**Decision.** Every app service (auth, content, shell-ws) listens on a **unix domain
socket** under `/run/euler/`; Caddy reverse-proxies to it
(`reverse_proxy unix//run/euler/<svc>.sock`). No app service binds a TCP port — only
Caddy is network-bound (`:443`).

| Service | Socket | Runs as |
|---|---|---|
| auth | `/run/euler/auth.sock` | `euler-auth` |
| content | `/run/euler/content.sock` | `euler-content` |
| shell-ws | `/run/euler/ws.sock` | `euler-ws` |
| maintenance (static) | — served by Caddy directly | `euler-caddy` |

**Why.** Filesystem permissions become OS-enforced access control (only members of
`euler-web` can `connect()`); there is no port registry to maintain; and the services
have **zero network surface** — nothing to port-scan, and no `0.0.0.0` mis-bind one
typo away. Marginally lower latency also helps the streaming shell WS. The one cost —
socket lifecycle (create the dir, unlink a stale socket, set owner/mode) — is absorbed
by systemd (`RuntimeDirectory=`) under DD-3.

**Health probes.** The Phase-1 health endpoint is **Caddy-native** (`respond
/healthz 200`), so it needs no socket. Per-service probes use
`curl --unix-socket /run/euler/<svc>.sock http://x/healthz`.

### DD-2 · Service-user strategy = dedicated users + shared group

**Decision.** One shared group **`euler-web`**, and a dedicated system user per
service: **`euler-caddy`**, **`euler-auth`**, **`euler-content`**, **`euler-ws`**,
plus **`euler-proxy`** for the Squid egress (Phase 2). Each *app* service's socket is
`owner=euler-<svc>`, `group=euler-web`, mode `0660`, in the `root:euler-web` runtime
dir `/run/euler`. Caddy runs as `euler-caddy` (a member of `euler-web`) so it can
`connect()` to every upstream socket; its unit also grants `CAP_NET_BIND_SERVICE` to
bind `:443` without root, and the TLS cert/key are readable only by `euler-caddy`.
`euler-proxy` owns no `/run/euler` socket — Squid is a forward proxy reached via
`HTTPS_PROXY`, not a Caddy upstream — so it stays outside `euler-web`.

**Why.** DD-1's isolation is only real across **distinct uids** — same-user processes
can always reach each other's sockets. Separate users give each service its own blast
radius: a compromised service cannot read another's files, send it signals, or inspect
its memory, and the highest-risk `euler-ws` (RCE by design) is fully separated.

**Scope note.** A single shared `euler-web` group means any group member could — in
principle — also `connect()` to a peer's socket; the guards against direct
service-to-service calls remain uid separation plus `forward_auth` at the edge. If
strict socket-level peer isolation is later needed, split into per-service groups
(`euler-auth-fe`, …) each containing only Caddy + the owning user. Deferred as a
refinement; not needed for the phased build.

### DD-3 · Edge orchestrator = `frontend.sh` + root-owned systemd

**Decision.** Replace the separate `scripts/setup/caddy.sh` and
`scripts/setup/acme.sh` with a single **`scripts/setup/frontend.sh`** exposing full
**`install` / `uninstall` / `upgrade`** (plus `status`) for the whole edge. It:

1. creates the `euler-web` group and the `euler-*` service users (idempotent);
2. installs Caddy (apt) and acme.sh **as root** (`/root/.acme.sh`), so the renewal
   cron is unattended;
3. issues + deploys the TLS cert via acme.sh DNS-01 into **`/etc/euler/tls`**
   (`root:euler-web`, key `0640`) so `euler-caddy` can read it; the renewal hook
   re-applies that ownership/mode and reloads the edge;
4. generates the **`/etc/euler/Caddyfile`** unix-socket router (path → `unix//run/euler/*`
   upstreams, the `forward_auth` block, security headers + fallback CSP);
5. installs the **root-owned systemd *system* unit** `euler-caddy.service` in
   `/etc/systemd/system` (`WantedBy=multi-user.target`, so the edge comes up at
   **boot**).

**Per-concern kits.** `frontend.sh` owns the *edge* (Caddy) — its `renew` reissues the
cert (no DNS creds needed; acme.sh caches them) and `status` reports the acme.sh renewal
cron + next renewal. Each other concern gets a **sibling setup script of the same shape**
as its phase lands — `egress.sh` → `euler-proxy.service` (Squid, Phase 2), `ddns.sh` →
`euler-ddns.timer` (dynamic DNS, public access only), then the app services
(`euler-auth` / `euler-content` / `euler-ws`) — each creating its own user and root-owned
unit. A `make` umbrella (`install-frontend`, `install-egress`, `install-ddns`, …)
composes them; every service stays independently installable and restartable.

**Config location.** The edge's config and secrets live under **`/etc/euler`**, not in
the repo: the dedicated `euler-caddy` user cannot traverse the repo owner's `0750` home
dir, so a repo-local Caddyfile/key would be unreadable. `frontend.sh` therefore writes
`/etc/euler/Caddyfile` and `/etc/euler/tls/`, fully decoupling the edge from the
checkout. (Static assets the edge serves — e.g. the Phase-3 maintenance page — are
likewise deployed under `/etc/euler`.)

**Privilege model.** Because the units live in **root's** systemd and run as the
locked-down `euler-*` users, lifecycle is privileged: `start` / `stop` / `restart`
require **`sudo`** (`sudo systemctl … euler-*`, or `sudo frontend.sh {start,stop}`).
This supersedes the old relocatable, user-owned `caddy-euler.service` (which ran as the
repo owner and needed no sudo) and the detached-process + `fcntl.flock` fallback — the
edge now **assumes systemd** (present on both dev and the deployment host).

### DD-4 · No service runs as root (acme + ddns get dedicated users)

**Decision.** No `euler-*` service runs as root. Phases 1–2 left two exceptions —
acme.sh and the DDNS updater both ran as **root** — and this closes them with dedicated,
nologin system users, each in its own group (outside `euler-web`):

| Service | User | Code | Config | Renewal/run |
|---|---|---|---|---|
| cert issue/renew | `euler-acme` | acme.sh in `/usr/local/share/euler-acme` | caches its own state; DNS creds passed at issue time | `euler-acme.timer` (daily) |
| dynamic DNS | `euler-ddns` | `/usr/local/bin/euler-ddns` | `/etc/euler/ddns.env` (`root:euler-ddns 0640`) | `euler-ddns.timer` |

**Cert reload without root.** The reload of `euler-caddy` uses **Caddy's admin API**
(`caddy reload --config /etc/euler/Caddyfile`, loopback `:2019`), not `systemctl` — so a
non-root `euler-acme` triggers it. The Caddyfile is `0644` (non-secret) so `euler-acme`
reads it without joining `euler-web`.

**Cert deploy without chown.** `/etc/euler/tls` is `euler-acme:euler-web`, **`setgid`
(2750)** — acme.sh (as `euler-acme`) writes `server.{crt,key}` there and they inherit
group `euler-web`; the reloadcmd `chmod`s the key `0640`, so `euler-caddy` reads it via
the group. No `chown`, no root.

**Renewal on a timer, not a crontab.** acme.sh is installed `--nocron`; renewal runs from
`euler-acme.timer` (a root-owned systemd timer running `acme.sh --cron` as `euler-acme`),
consistent with DD-3 and sidestepping system-user crontab quirks.

**Config source.** `keys/.env` stays the **install-time authoring** source of truth; the
installer (repo owner + sudo) deploys the *scoped* runtime config into `/etc/euler`
(`edge.env` = FQDN + email; `ddns.env` = FQDN + name.com creds), which the dedicated users
read — so no runtime service needs the repo checkout. `/usr/local/bin/euler-ddns` is a
copy of the updater for the same reason. This also scopes secrets: `euler-ddns` sees only
the name.com creds, never the full `keys/.env` (Anthropic key, SMTP password).

### DD-5 · App runtime = `/opt/euler` system venv, framework = aiohttp + Jinja2

**Decision.** The Python app services (`euler-auth` first, then content/ws) run from a
**root-owned system venv at `/opt/euler`**, *not* from the repo checkout: the dedicated
service users cannot traverse the repo owner's `0750` home (same constraint that put the
edge config in `/etc/euler`, DD-3). The installer (`scripts/setup/auth.sh`, repo owner +
sudo) does `pip install .` (the `web` extra) into `/opt/euler/venv`, and the unit runs
`ExecStart=/opt/euler/venv/bin/python -m solver.web.auth`. `upgrade` re-installs from the
repo. The **framework is aiohttp + Jinja2** (autoescape on), resolving the
[Framework/templating](#framework--templating) open decision — one framework shared with
the shell service; Jinja replaces the homegrown string templating.

**System paths (app runtime).**

| Path | Owner / mode | Purpose |
|---|---|---|
| `/opt/euler/venv/` | `root:euler-web` `0755` | the deployed venv; `solver` + `web` deps `pip install`ed here. Service users execute it; only root writes it (install/upgrade). |
| `/opt/euler/venv/bin/python` | `root:euler-web` `0755` | interpreter the units run (`-m solver.web.<svc>`). |
| `/run/euler/` | `root:euler-web` `0770` (`RuntimeDirectory`, tmpfs) | shared socket dir; each service creates its own `*.sock` (`0660 euler-<svc>:euler-web`) so `euler-caddy` connects and no peer can bind another's name. |

Jinja **page templates** ship as package data inside the venv
(`solver/web/templates/*.html`); **static assets** (CSS/JS) stay in the repo-root
`web-content/` tree deployed to `/etc/euler/web-content` and served by Caddy under
`/assets/*` (Phase 3) — so rendered pages reference `'self'` assets and the CSP holds.

**Why not run from the repo.** Rejected for the DD-3 reason: it would require opening
`/home/vikas` to the service uids, widening a compromised service's read surface to the
entire home dir. A system venv keeps runtime fully decoupled from the checkout.

### DD-6 · Auth state is `euler-auth`-private; admin ops go through an admin API

**Decision.** All auth state is owned by **`euler-auth` alone** (`0600`, under the unit's
`StateDirectory=/var/lib/euler-auth`); no file is shared with the repo owner. The admin
shell commands — `users add` / `list` / `enable` / `disable` / `remove` (run as *you*) —
never touch those files; they call an **admin API on the auth service** over a socket,
authenticated by `X-Admin-Token`. Admins **cannot** reset passwords (reset is self-service,
[DD-7](#design-decisions)). The service is the **sole reader/writer** of its state.

**System paths (auth state + config).**

| Path | Owner / mode | Purpose |
|---|---|---|
| `/var/lib/euler-auth/users.json` | `euler-auth:euler-auth` `0600` | SRP verifier DB (`{salt, verifier, profile, terms_version, terms_accepted_at, disabled}` per email). Never a password. |
| `/var/lib/euler-auth/pending.json` | `euler-auth:euler-auth` `0600` | in-flight invites/resets keyed by `hash(link-token)` (see [DD-7](#design-decisions)). |
| `/var/lib/euler-auth/remember.json` | `euler-auth:euler-auth` `0600` | remember-me `selector → (email, HMAC(validator), expiry)`, rotated on use. |
| `/var/lib/euler-auth/session-secret` | `euler-auth:euler-auth` `0600` | 32-byte HMAC key for remember-me; created on first start. |
| `/etc/euler/auth.env` | `root:euler-auth` `0640` | scoped runtime config: `EULER_BASE_URL`, `EULER_ADMIN_TOKEN`, `TERMS_VERSION`, `EULER_SMTP_RELAY` (loopback `host:port` of the mail relay). Deployed from `keys/.env` (authoring source, DD-4). |

Sessions themselves are **in-memory** (per-process): a restart drops live sessions, and
remember-me cookies restore them — matching the parked design. `euler-auth` reads only
`auth.env` — never the full `keys/.env`, and (per [DD-8](#design-decisions)) **not even the
SMTP credentials**: it submits mail to a loopback relay that holds them. So a compromised
auth service leaks neither the Anthropic key nor the Gmail app password.

**Admin plane.** The admin API is **local-only** — a dedicated admin listener
(`/run/euler/auth-admin.sock`, `euler-auth:euler-adm 0660`; you join `euler-adm`), **never
routed through Caddy**, so admin endpoints have zero public surface. `X-Admin-Token`
(shared secret in `keys/.env` ↔ `auth.env`) is a second check. The public `auth.sock`
(via Caddy) exposes only login / registration / `forward_auth`.

**Why an API over shared files.** Chosen over group-writable files (the rejected
alternative): keeps auth state single-writer and `0600`, so no other uid — not even a
mis-scoped admin tool — can corrupt or read the verifier DB. The admin CLI is a thin HTTP
client; the service owns all invariants (validation, sweeping, state transitions).

### DD-7 · Registration = invite link → Terms → OTP → SRP password

**Decision.** Registration is **invite-only and two-channel**. An admin mints an invite; the
invitee proves live control of the mailbox (OTP) and accepts Terms before a password is
ever set. All secrets are stored hashed; every step is single-use and time-boxed. The same
link→OTP→password pipeline serves password **reset** (`kind=reset`, skipping the Terms
step) — but reset is **self-service** (a user initiates it from `/forgot`); admins never
reset passwords (they only add / enable / disable / remove accounts — see [DD-6](#design-decisions)).

**Flow.**

1. **Invite** — admin runs `users add <email> --profile <p>`; the shell calls the admin API
   (`POST /admin/users`). The service creates a `pending.json` record keyed by
   `hash(link-token)`: `{email, profile, kind=register, state=invited, expiry=+7d}`, and
   emails `https://<FQDN>/register?token=<link-token>` (32-byte URL-safe token). No user
   record exists yet.
2. **Open link** — invitee `GET /register?token=…`. Valid + unexpired + `state=invited` →
   render the registration page (email shown read-only, **Terms of Use**, "I accept" +
   "email me a code"). Invalid/expired → generic error page (no enumeration).
3. **Accept Terms + request OTP** — `POST /register/otp` (token, `accepted=true`). Service
   records `terms_version` + timestamp, generates a **6-digit OTP**, stores
   `hash(otp)` + `otp_expiry=+10min` + `attempts=0`, sets `state=otp_sent`, and emails the
   OTP. Re-renders with an OTP field. Resends are rate-limited/capped.
4. **Verify OTP** — `POST /register/verify` (token, otp). `hash(otp)` match, unexpired,
   `attempts<5` → `state=verified`. Wrong/expired → decrement; **5 failed tries invalidate
   the OTP** (a fresh one must be requested).
5. **Set password (SRP)** — the browser derives `{salt, verifier}` client-side from a
   password meeting the policy (≥16 chars, 4 classes; the server never sees it) and
   `POST /register/complete` (token, salt, verifier). `state=verified` + valid token →
   create the `users.json` record (with the recorded Terms acceptance), **consume** the
   pending record (single-use), and land on **`/login`** (no auto-login).

**State machine.** `invited → otp_sent → verified → completed` (records sweep on the 7-day
link expiry; the OTP sweeps on its 10-minute expiry independently).

**Token vs OTP.** The **link token** (32 bytes, 7-day, single registration session) proves
possession of the invite; the **OTP** (6 digits, 10-min, few attempts) proves *live* control
of the mailbox at completion time and gates Terms→password. Both are stored only as hashes;
neither is ever logged. Per-token and per-IP rate limits guard OTP request/verify; generic
responses avoid account enumeration.

**Self-service reset.** A user starts reset at `/forgot` (enters their email). If the
account exists and is enabled, the service mints a `kind=reset` pending record and emails a
`/reset?token=…` link; the link → OTP (10-min, 5-try) → set-password steps are identical to
registration but skip Terms. Responses are **generic regardless of whether the email exists**
(no enumeration), and the endpoint is rate-limited per IP. Admins have **no** reset verb.

**Confirmed parameters.** OTP = **6 digits, 5 tries** then invalidate; completion lands on
**`/login`** (no auto-login); Terms text at **`web-content/terms.html`**, versioned by
`TERMS_VERSION` (acceptance recorded on the user record).

### DD-8 · Kernel-enforced egress firewall + loopback mail relay

**Decision.** "Egress only via Squid" is enforced at the **kernel**, not just by the
`HTTPS_PROXY` env var (which a compromised process can ignore). Two layers:

1. **systemd per-unit IP filter** — every loopback-only app unit (`euler-auth`,
   `euler-content`, `euler-ws`) carries `IPAddressDeny=any` + `IPAddressAllow=localhost`,
   so the app tier can reach **only loopback** (their `/run/euler` sockets, the Squid proxy
   at `127.0.0.1:3128`, and the loopback mail relay). This defense travels with the unit.
   `euler-caddy` is the exception — it terminates public inbound `:443`, which the systemd
   filter (it applies to both directions) would block; its egress lock comes from layer 2:
   `ct state established,related` permits its replies while any *NEW* outbound it initiates
   hits the final drop.
2. **host nftables owner-match** (`scripts/setup/firewall.sh` → `euler-firewall.service`,
   ruleset in `/etc/euler/nftables.conf`) — a dedicated `table inet euler` with an
   **egress-only** (`hook output`) chain that, **scoped to the `euler-*` uids**, permits
   loopback and only the specific `(uid, port)` egress each service genuinely needs, then
   drops the rest:

   | uid | allowed egress |
   |---|---|
   | `euler-proxy` (Squid) | `tcp dport {80,443}` — the **only** service with real internet; its L7 domain allowlist still applies |
   | `euler-acme` | `tcp dport 443` (ACME + DNS-provider API) |
   | `euler-ddns` | `tcp dport 443` (name.com API, ipify) |
   | `euler-smtp` (relay) | `tcp dport 587` (Gmail submission) |
   | `euler-acme`,`euler-ddns`,`euler-proxy`,`euler-smtp` | `udp/tcp dport 53` (DNS, unless the host resolver is on loopback) |
   | all `euler-*` | `oif lo` (loopback); **everything else dropped** |

   The chain uses `policy accept` and drops **only** the enumerated `euler-*` uids (a final
   `skuid { … } drop`), so non-service traffic — SSH, root, your shell — is untouched (no
   lock-out risk). The ruleset is **egress-focused**; host `INPUT` policy is left alone
   (inbound `:443` is Caddy's; SSH stays reachable). Per-service network namespaces (DD's
   rejected option C) remain a future hardening.

**Mail relay (`euler-smtp`).** So the app tier needs **no** direct-internet exception, OTP/
invite mail goes through a small **loopback submission relay** running as a dedicated
`euler-smtp` user (its own group, outside `euler-web`): it listens on **`127.0.0.1:8025`**
(the `EULER_SMTP_RELAY` value) and is the **sole holder of the Gmail credentials** and the
**sole uid permitted `:587`**. `euler-auth` submits via loopback SMTP with no credentials of
its own; the relay **forces the envelope sender** to `SMTP_ADDRESS` and never logs message
bodies (they carry OTPs). A firewall **relay guard** additionally bars every other euler-*
uid from connecting to `:8025`, so a compromised `euler-ws`/`euler-content` cannot send mail.
Relay config (`SMTP_ADDRESS`, `SMTP_APP_PASSWORD`) is scoped to the relay
(`/etc/euler/smtp.env`, `root:euler-smtp 0640`), deployed from `keys/.env` (DD-4).

**System paths (firewall + relay).**

| Path | Owner / mode | Purpose |
|---|---|---|
| `/etc/euler/nftables.conf` | `root:root` `0644` | generated `table inet euler` egress ruleset |
| `euler-firewall.service` | root-owned unit | loads/flushes the euler ruleset at boot |
| `/etc/euler/smtp.env` | `root:euler-smtp` `0640` | Gmail creds — read **only** by the relay |
| `euler-smtp.service` | root-owned unit | loopback submission relay (`User=euler-smtp`) |

**Why.** Without this, "plaintext must never leave the repo" and the Squid allowlist rest on
an environment variable. The firewall makes Squid the *only* path to the internet for the
app tier at the packet level; the relay keeps the SMTP exception off the app uids and the
Gmail password out of every service but one.

### DD-9 · Identity, authentication, and masquerade prevention

**Decision.** The auth service is built **fresh** as the **`solver/web/auth`** sub-package
(the parked `old-web-server` branch remains a *cherry-pick source* — the SRP-6a math,
policy constants, and rate limiter port cleanly — but the stores are re-implemented on the
DD-6 state paths). The current `keys/` web-auth store (`.users.json`, `.pending.json`,
`.remember.json`, `.session-secret`) is **not ported**: state starts empty in
`/var/lib/euler-auth`, and the live service is proven by minting invites and registering
users afresh (DD-7). Those `keys/` dotfiles are retired once Phase 4 lands. Identity
resolution (`solver/utils/identity.py`) is redesigned around **three planes**, each with an
explicit voucher:

| Plane | Who vouches | Mechanism |
|---|---|---|
| Web request | auth service | SRP session cookie → `forward_auth` → `200 + X-User, X-Profile` |
| Web shell (PTY child) | auth service | **one-time shell ticket**, redeemed over `auth.sock` at startup |
| Local terminal | the OS | `os.getuid()` **owns the repo checkout** → `admin` |

**Web authentication (requests).** As designed in [authentication.md](authentication.md):
browser-side SRP-6a (RFC 5054 2048-bit group, `g=2`, SHA-256; server stores only
`{salt, verifier}`), in-memory sessions + rotating remember-me (DD-6), invite → Terms →
OTP → SRP registration and self-service reset (DD-7). The `forward_auth` endpoint returns
`200` with **both `X-User`** (email) **and `X-Profile`** (`admin`/`user`/`guest` from the
user record) or `401`. Caddy copies those two response headers onto the proxied request
and **deletes any client-supplied `X-User`/`X-Profile` first**, so an identity header can
never be injected from outside; content/ws trust the headers because their sockets are
reachable only via Caddy (DD-1/DD-2).

**Web shell identity (the shell ticket).** Every PTY shell runs as uid `euler-ws` (no
root, so no per-user setuid), and `/proc/<pid>/environ` is readable by same-uid processes
— so **nothing carried in the environment can be the credential**: a signed-but-reusable
assertion could be replayed by any other web user's shell. Instead, identity transfers by
a consumable ticket:

1. On WS attach, the ws service forwards the user's session **cookie** to
   `POST /shell-ticket` on `auth.sock`; the auth service validates the session and mints a
   **single-use, 60-second** ticket bound to `(email, profile)` (held in memory, stored
   hashed, never logged).
2. The ws service forks the PTY child with `SOLVER_TICKET=<ticket>`
   (plus `SOLVER_USER=<email>` for display only — it grants nothing).
3. At startup the shell **redeems** the ticket over `auth.sock`
   (`POST /shell-ticket/redeem`); redemption consumes it and returns the authoritative
   `(email, profile)`. Missing/expired/reused ticket → shell startup aborts.

Minting requires a live session cookie (which a shell user does not hold), and redemption
is single-use — so a web user re-execing `solver` inside their PTY can obtain no identity
but their own. The `/shell-ticket*` endpoints are **not routed by Caddy** (socket-peer
only), keeping them off the public surface entirely.

**Local authentication.** The local trust anchor becomes precise: the fallback that grants
the **`admin`** profile applies **only when the process uid owns the repo checkout**
(`os.getuid() == stat(root_dir).st_uid`) — physical/login access to *the checkout* is the
trust, stated exactly. Service uids never fall through to admin. The old
**assume-an-identity** path (`export SOLVER_USER=…` verified against `keys/.users.json`,
plus the `keys/.user-email` / `keys/.env` identity inputs) is **dropped**: the user DB is
now `euler-auth`-private so there is nothing local to verify against, and exercising a
lesser profile is done through a real web login instead.

**Resolution order (new `identity.py`).**
1. `SOLVER_TICKET` set → redeem over `auth.sock` → `(email, slug, profile)`;
   redemption failure aborts startup.
2. else uid owns the checkout → `(getpass.getuser(), slug, 'admin')`.
3. else → abort (`SystemExit`); there is no anonymous fallback.

**Masquerade vectors → guards.**

| Vector | Guard |
|---|---|
| Browser sends its own `X-User`/`X-Profile` | Caddy strips inbound copies; only `forward_auth` response headers are forwarded; app sockets unreachable except via Caddy |
| Web user re-execs `solver` with a chosen `SOLVER_USER` | env is display-only; identity requires a ticket; the local fallback refuses non-owner uids |
| Replaying another shell's credential from `/proc/*/environ` | tickets are single-use — already consumed by the victim's own startup |
| Bare `solver` as a service uid claiming admin | admin fallback requires the checkout-owner uid |
| Minting a ticket from inside a PTY (same uid *can* connect to `auth.sock`) | minting demands a live session cookie the shell user does not possess |
| Admin-plane abuse | local-only `auth-admin.sock` (`euler-adm` group) + `X-Admin-Token`, never routed by Caddy (DD-6) |

**Residual risk (accepted).** All web shells share uid `euler-ws`: a hostile shell user
with arbitrary code execution could attack *sibling* shells of that uid (Yama
`ptrace_scope=1` blocks non-ancestor ptrace; files and sockets writable by the uid remain
shared). The standing controls are authorization (`!`/`bash` stays **admin-only** in
`commands.csv`) and the fact that identity never rests on the uid — masquerade against the
auth service stays impossible even under same-uid compromise. Per-user helper uids or
namespaces remain a Phase-6 hardening option.

---

## Framework / templating

The three options are not the same kind of thing — Jinja2 is a *templating engine*;
aiohttp and FastAPI are *frameworks*. The real question is **(a) which framework
serves the content service** and **(b) whether homegrown string templating is
replaced by Jinja2.** (The shell service stays aiohttp regardless — its PTY/WS code
already works; rewriting it buys nothing.)

| Option | What it means | Assessment |
|---|---|---|
| **aiohttp only** | Keep aiohttp; keep the current `template.replace('{{TITLE}}', …)` + manual `html.escape` string templating. | ✗ This homegrown engine is exactly what we're escaping — no layout inheritance, no partials, **no autoescaping** (an XSS footgun). Rejected. |
| **aiohttp + Jinja2** (via `aiohttp-jinja2`) | Keep aiohttp as the one framework across content + shell; use Jinja2 for all HTML. | ✅ **Recommended.** Template inheritance (`base.html` → page blocks) and partials give the code reuse you asked for; **autoescape-on-by-default** is an output-side XSS defence for free; one framework/middleware stack shared with the shell service (CSP, auth headers, logging). |
| **FastAPI (+ Jinja2)** | Switch the content service to Starlette/FastAPI, render via `Jinja2Templates`. | ➖ FastAPI's headline value (pydantic-typed JSON bodies + OpenAPI) is for **JSON APIs**, which is precisely what we're moving *away* from. For SSR its Jinja integration is no better than `aiohttp-jinja2`, and it adds starlette + pydantic + uvicorn weight and a second framework alongside the aiohttp shell service. Reach for it only if a typed JSON API becomes a first-class product. |

**Recommendation: aiohttp + Jinja2.** Resolve the three-way as "aiohttp stays the
framework, Jinja2 replaces homegrown templating." Rendering contract:

- `base.html` owns `<head>` (shared `common.css`, `solver-theme.css`, vendored JS),
  the header/nav include, and the footer. Every page `{% extends "base.html" %}`.
- Autoescape **on**. Any pre-sanitised HTML is injected through an explicit
  `| safe` only after passing [nh3](#nh3).
- A route renders either the **whole page** or a **named block/fragment** of the
  same template (via `jinja2-fragments` or block rendering), so a full load and a
  live update share one source of truth.

---

## Liveness: server-rendered, feels live

"Feels live" has two regimes; both keep the server as the sole renderer:

1. **Request-driven updates** (edit → save → show validation panel; navigate a
   file list; run a quick eval). → **[htmx](#htmx)**: `hx-get`/`hx-post` fetch a
   **rendered HTML fragment** (a Jinja block) and swap it in. No client JSON, no
   client templating.
2. **Server-pushed updates** (benchmark progress, long command output). → **SSE**
   (htmx SSE extension) or reuse the existing **shell WebSocket**. Prefer SSE for
   one-way content-service progress; reserve the WS for the interactive shell.

## htmx

**Benefits**
- Server stays the only renderer: fragments are Jinja blocks, so full pages and
  live updates reuse the same templates — maximal code reuse, zero client-side
  duplication of markup.
- "Live" feel with **no framework and no build step**: ~14 kB, vendorable into
  `web-content/vendor/` exactly like `xterm.js`/`codemirror` today (pinned +
  SRI + `LICENSES` entry).
- **Security posture improves**: no client-side string→DOM assembly means no
  DOM-XSS class; all escaping is Jinja autoescape, server-side. Smaller JS surface
  than the current per-page `*.js` fetch/populate scripts, several of which can be
  deleted.
- Progressive enhancement: forms/links still work without JS; htmx enhances them.

**Consequences**
- New concept to hold (`hx-*` attributes, swap targets, fragment endpoints).
  Discipline needed so fragment routes don't sprawl — standardise on
  "one template, render whole or a named block."
- **CSP interaction (must design for):** with `script-src 'self'` and **no**
  `unsafe-inline`, use `hx-*` attributes (fine — they are not inline script) and
  **avoid `hx-on:` inline handlers**. htmx also injects an indicator `<style>`
  unless disabled — set `htmx.config.includeIndicatorStyles = false` and ship the
  indicator CSS in `common.css`, so `style-src 'self'` needs no `unsafe-inline`.
- Server-push liveness needs the SSE (or WS) extension — one more vendored piece.

**Verdict:** adopt. It is the lowest-cost way to get server-rendered liveness and
it *strengthens* the CSP/XSS story rather than fighting it.

## nh3

Context: the current edit path already validates `.py` (flake8 + autofix), `.c`
(compile), and `.json` (parse/reserialise) with reject-and-restore, but **writes
`.html` verbatim** (`app.py` `_save_content`, the `target.suffix == '.html'`
branch) — a **stored-XSS hole**, since `notes.html` is served back and rendered.
`nh3` is the Rust/Ammonia HTML sanitiser (the maintained successor to the dead
`bleach`).

**Benefits**
- Closes the hole with an **allowlist** sanitiser on save: strip `<script>`,
  `on*` handlers, `javascript:`/`data:` URLs, unknown tags/attrs. Fast, memory-safe.
- Drops straight into the existing `_save_content` normalise/reject pattern
  (sanitise → if changed, either store the clean version like JSON reindent, or
  reject-and-restore).
- **Defence in depth** with the locked CSP: nh3 gates what is *stored*, CSP blocks
  what would *execute* at runtime — independent layers.

**Consequences**
- **Native dependency.** nh3 ships as a compiled (Rust) wheel — *verify a
  `cp314` wheel exists for this project's Python 3.14 before committing*, else the
  install needs a Rust toolchain. This is the main friction for the dep-management
  kit; pin it and gate install on wheel availability.
- **Lossy by design.** An allowlist strips author-intended markup. `notes.html`
  uses tables, code blocks, and **MathJax** (vendored) — tune the allowlist to pass
  those (MathJax delimiters survive as text; do **not** allow raw `<script>`).
  Budget time to curate and test the allowlist against real notes.
- **Two linters?** There is already an *advisory* `html5lib` check in the editor
  (well-formedness feedback). Decide: keep `html5lib` advisory (author feedback) +
  `nh3` as the enforcing save gate, **or** drop `html5lib`. Recommend keeping both
  with distinct roles.

**Alternative worth weighing:** author notes in **Markdown**, not raw HTML —
`app.py` already renders Markdown (`markdown-it-py`). Then the edit path never
accepts raw HTML; you render server-side and still run nh3 over the *output*. This
sidesteps hand-authored HTML entirely, at the cost of changing how the AI skill
emits notes. Flag for a separate decision.

**Verdict:** adopt nh3 as the save-time gate (pending the cp314-wheel check);
evaluate the Markdown-authoring alternative for `notes.html` independently.

## Content-Security-Policy

Locked: **every served page carries a CSP.** Design:

- Emitted by an **app middleware** (content + auth services), not only Caddy,
  because a strict policy uses a **per-response nonce** for any unavoidable inline
  `<script>`/`<style>`; the app that renders the page must mint the nonce and stamp
  it into both the header and the template.
- Baseline: `default-src 'self'; script-src 'self'; style-src 'self'; img-src
  'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none';
  object-src 'none'`. No `unsafe-inline`, no `unsafe-eval`.
- **Caddy** adds the transport-level headers that don't need per-response state
  (HSTS, `X-Content-Type-Options`, `Referer-Policy`) and can set a **fallback CSP**
  for purely static responses (the maintenance page, vendored assets).
- Vendored JS (htmx, xterm, codemirror, MathJax) is served from `'self'`, so
  `script-src 'self'` covers it. MathJax may need `style-src 'self'` +
  its nonce; confirm during the content phase.

---

## The maintenance kit (per-feature contract)

Every phase below ships **all** of these before it is "done". This mirrors the
existing `scripts/setup/caddy.sh` convention (idempotent, header block documenting
*why*, subcommands).

1. **Design note** — a section in this doc or a dedicated `docs/*.md`, cross-linked.
2. **Dependency management** — `install` / `uninstall` / `update` for that feature's
   deps:
   - *Python deps* (Jinja2, nh3, aiohttp-jinja2): pinned in a `pyproject` optional
     group + a `check` that verifies importability and wheel availability.
   - *Vendored browser assets* (htmx, SSE ext): a vendoring script that downloads a
     **pinned** version into `web-content/vendor/`, records the **SRI hash**,
     and appends to `vendor/LICENSES` — the pattern already used for
     `xterm.js`/`codemirror`/`mathjax`.
   - *System deps* (caddy, squid): apt repo + package, plus `euler-web` group /
     `euler-*` user creation — all via the idempotent `frontend.sh` (DD-3).
3. **Configuration** — generator for any host-specific config (Caddyfile, Squid
   allowlist, service env), written to a system path (`/etc/euler`, so the service
   users can read it) or gitignored in-repo when repo-local, generated at install from
   the single-source-of-truth `keys/.env` (e.g. the FQDN `EULER_TLS_DOMAIN`) or a prompt.
4. **Lifecycle** — `start` / `stop` / `status` / `restart` via a **root-owned systemd
   *system* unit per service** (`euler-<svc>.service`, boot-enabled), so lifecycle
   needs `sudo` (DD-3). The edge assumes systemd; the old detached-process +
   `fcntl.flock` fallback is dropped. Each service is independently restartable.
5. **Health probe** — a `status` that reports actually-serving (flock/HTTP ping),
   not just "process exists".

An **umbrella orchestrator** (`scripts/setup/frontend.sh`, or a `make web-*` target)
composes the per-service lifecycles so the whole stack starts/stops/reports as one,
while each service remains independently operable.

---

## Phases

Built strictly in order; each is independently runnable and shipped with its full
[maintenance kit](#the-maintenance-kit-per-feature-contract). The stack is useful
and demonstrable at the end of every phase.

### Phase 1 — Caddy + ACME (edge)
- **Deliver:** public `:443` edge terminating TLS, auto-renewing cert, reverse-proxy
  skeleton routing to (initially nothing but) a Caddy-native health endpoint
  (`respond /healthz 200`). Security headers + fallback CSP for static responses.
- **Build:** the `scripts/setup/frontend.sh` orchestrator (folding in the old
  `caddy.sh` + `acme.sh`): create the `euler-web` group + `euler-caddy` user, install
  Caddy + acme.sh (as root), issue/deploy the cert to `/etc/euler/tls` (readable by
  `euler-caddy`), generate the **`/etc/euler/Caddyfile`** unix-socket router (path →
  `unix//run/euler/*` upstreams, `forward_auth` block stubbed, health endpoint), and
  install the **root-owned** `euler-caddy.service`
  (see [Design decisions](#design-decisions) DD-1…DD-3).
- **Kit:** `frontend.sh install/uninstall/upgrade`; Caddyfile generator; root-owned
  systemd unit (`euler-caddy.service`, boot-enabled, `sudo` to start/stop); `status`
  via cert + HTTP ping (`curl --unix-socket` once app services exist).

### Phase 2 — Squid (egress) ✅
Built as `scripts/setup/egress.sh` (sibling to `frontend.sh`).
- **Deliver:** Squid forward proxy on loopback `127.0.0.1:3128` with a **domain
  allowlist** (`api.anthropic.com`, `.projecteuler.net`, `.github.com`,
  `.githubusercontent.com`); default-deny. Runs as the dedicated `euler-proxy` user
  (DD-2), in its own group **outside** `euler-web`. Config in `/etc/euler-proxy`
  (`squid.conf` + the editable `squid.allowlist`).
- **Wire:** `HTTPS_PROXY`/`HTTP_PROXY` written to `/etc/euler/egress.env`, which the
  app-service units load via `EnvironmentFile=` so AI features, the problem scraper,
  and `gh` egress only via Squid — operationalising the "plaintext must never leave the
  repo" rule at the network layer.
- **Kit:** `egress.sh install/uninstall/upgrade/status/reload`; allowlist generator
  (preserves operator edits); root-owned, boot-enabled `euler-proxy.service`; `status`
  probes an allowed and a denied domain through the proxy.

### Phase 3 — Maintenance page (static) ✅
Folded into `scripts/setup/frontend.sh` (no new script — the edge orchestrator owns it).
- **Deliver:** a single static **"site under maintenance"** page served through Caddy
  end-to-end — proves TLS, routing, headers, and CSP fallback on a real response. No
  app framework yet. Reusable later as the holding page Caddy serves when an upstream
  is down or during a deploy.
- **Establishes:** the `web-content` static layout (repo-root `web-content/`:
  `maintenance.html` + `assets/maintenance.css`) and the CSP baseline the app services
  will inherit — the page is authored to pass the edge fallback CSP
  (`default-src 'self'; style-src 'self'`): one same-origin stylesheet, **no** inline
  styles or scripts.
- **Wiring:** `frontend.sh` deploys the repo `web-content/` tree to
  `/etc/euler/web-content` (`root:euler-web`, `0644`/`0755`) so `euler-caddy` can read
  it, and generates a Caddyfile where `/healthz` and `/assets/*` are served directly
  while **every other request falls through to the maintenance page** (HTTP `503` +
  `Retry-After`, its CSS still served `200` so the page renders styled). The future
  content/ws/auth upstreams are commented stubs; a `handle_errors` block reuses the
  same holding page so it also shows whenever a later-phase upstream is down.
- **Kit:** the page + its assets; no new runtime dep; deployed and wired into Caddy
  routing by `frontend.sh install`/`upgrade` (`make install-frontend`/`upgrade-frontend`).

### Phase 4 — Auth service
**Status: 🔨 in progress — build-order step 1 shipped.** Design decisions
[DD-5](#design-decisions) (runtime + framework), [DD-6](#design-decisions) (state + admin
plane), [DD-7](#design-decisions) (registration flow), [DD-8](#design-decisions) (egress
firewall + mail relay) and [DD-9](#design-decisions) (identity + masquerade prevention)
are locked; this phase implements them.

**Build order** (each step independently landable/testable):
1. ✅ **`firewall.sh` + `smtp.sh` kits (DD-8)** — the host nftables egress ruleset
   (`euler-firewall.service`; per-uid, generated with only the euler-* users that exist,
   `reload` regenerates as later kits add users) and the `euler-smtp` loopback mail relay
   (`scripts/setup/euler-smtp.py`, stdlib-only, deployed to `/usr/local/bin/euler-smtp`),
   so the app tier is loopback-only from its first deploy and mail has a credential-scoped
   path out. `make install-firewall` / `install-smtp`; `smtp.sh test` sends a real probe
   mail; `firewall.sh status` probes an allowed and a dropped uid.
2. **`web` extra + `/opt/euler` deploy (DD-5)** — pin `aiohttp`/`aiohttp-jinja2`/`Jinja2`
   in the `web` optional group; `auth.sh` provisions the `euler-auth`/`euler-adm` identities
   and `pip install .[web]` into `/opt/euler/venv`.
3. **Fresh `solver/web/auth` + admin API (DD-6, DD-9)** — implement the package **from
   scratch** on `/var/lib/euler-auth` (`0600`): stores (users / pending / remember),
   sessions, the shell-ticket mint/redeem endpoints, the local admin listener, and the
   `users add/list/enable/disable/remove` shell commands. The parked branch is a
   cherry-pick source for the SRP-6a math, policy constants, and rate limiter only —
   the `keys/` web-auth store is **not ported** (no data migration): the service is
   live-tested by inviting and registering users afresh. Includes the `identity.py`
   redesign (ticket redemption; checkout-owner-uid admin anchor; the `SOLVER_USER` /
   `keys/.user-email` identity inputs dropped) and retiring the dead `keys/` dotfiles.
4. **Jinja pages + CSP-nonce middleware (DD-7)** — login / register / Terms / `/forgot`
   pages and the invite→OTP→SRP flow; the shared per-response-nonce middleware in
   `solver/web/`.
5. **Activate Caddy `forward_auth`** — gate all downstream routes through the auth socket
   (`/login`, `/register*`, `/reset*`, `/forgot`, `/assets/*`, `/healthz` public); the
   maintenance page remains the fallback until the content service lands.
- **Deliver:** aiohttp + Jinja2 auth service on `unix//run/euler/auth.sock`, running as
  `euler-auth` from the `/opt/euler` venv (DD-5). A **fresh `solver/web/auth`** build on
  the DD-6 state paths (parked branch cherry-picked for the SRP-6a math, policy, rate
  limiter only; no store port — see DD-9). Exposes SRP login/session/remember-me, the
  invite→Terms→OTP→SRP registration flow (DD-7), the **shell-ticket mint/redeem**
  endpoints (DD-9, socket-peer only), and a **`forward_auth` endpoint** returning
  `200 + X-User + X-Profile` or `401`; Caddy strips inbound identity headers and gates
  all downstream routes through it, with `/login`, `/register*`, `/assets/*`, `/healthz`
  public.
- **Deliver:** a **local admin listener** (`/run/euler/auth-admin.sock`, not routed
  through Caddy) for `users add/list/disable`, authenticated by `X-Admin-Token` (DD-6).
- **Deliver:** the **CSP middleware** (per-response nonce) lives in a shared
  `solver/web/` module and is imported by content later; the login / registration /
  Terms pages are the first Jinja-rendered pages.
- **Deliver (DD-8):** the kernel egress firewall (`scripts/setup/firewall.sh` →
  `euler-firewall.service`, per-uid nftables) and the loopback mail relay
  (`scripts/setup/smtp.sh` → `euler-smtp.service`), so the auth service is loopback-only
  from its first deploy and OTP/invite mail has a credential-scoped path out.
- **Kit:** `scripts/setup/auth.sh` (install/uninstall/upgrade/status) — create
  `euler-auth` + `euler-adm`, `pip install .[web]` into `/opt/euler/venv`, deploy
  `/etc/euler/auth.env` from `keys/.env`, provision `/var/lib/euler-auth`, install the
  root-owned `euler-auth.service` (with `IPAddressDeny=any`/`IPAddressAllow=localhost`);
  sibling `firewall.sh` + `smtp.sh` kits (DD-8); Python deps pinned in the `web` extra;
  `status` pings `forward_auth` over the socket; Caddy `forward_auth` block activated.

### Phase 5 — Content service
Built as four sub-steps; each independently shippable.

- **5a — Home, navigation, look & feel, behaviour.** `base.html` + partials, shared
  `common.css`/`solver-theme.css`, header/nav, **htmx** vendored and wired for
  fragment-swap navigation. A **placeholder panel stands in for the web shell** so
  the layout and liveness are demonstrable before Phase 6. Establishes the
  full-page-vs-block rendering contract.
- **5b — View paths.** Server-rendered summary, problem, code, and docs pages
  (replacing the skeleton+fetch `summary.js`/`problem.js`). Reads each problem's
  `solution_dir` (plaintext, incl. decrypted `solutions/private`). Deletes the
  client fetch/populate scripts as pages move server-side.
- **5c — Content validation.** Port and complete server-side write validation:
  reuse `.py`/`.c`/`.json` checks; **add the `.html` gate via [nh3](#nh3)**; keep
  reject-and-restore; decide `html5lib`-advisory vs nh3-enforcing split and the
  Markdown-authoring alternative for notes.
- **5d — Edit paths.** htmx-driven save/delete/eval/benchmark returning **rendered
  fragments** (validation panel, diagnostics, results); benchmark progress via SSE.
  Every write goes through 5c validation; every response carries CSP.
- **Kit:** Python deps (Jinja2, nh3) install/update/**cp314-wheel check**; htmx +
  SSE-ext vendoring (pinned + SRI + LICENSES); service env config; systemd unit +
  `status`; Caddy routes for content behind `forward_auth`.

### Phase 6 — Web shell
- **Deliver:** the PTY-backed interactive `solver` shell over WebSocket, **reusing**
  `web/pty_bridge.py` + `web/pty_manager.py` (one persistent shell per user, keyed by
  `SOLVER_USER`). Replace the Phase 5a placeholder with the live terminal
  (`xterm.js`, already vendored).
- **Isolation:** this is the highest-risk service (RCE by design) — run it as its own
  unit/user, egress only via Squid, and behind `forward_auth`.
- **Kit:** service env (SOLVER_USER wiring); systemd unit + flock `status` (the
  existing `cli.py` lifecycle model); Caddy `/ws` route behind `forward_auth`.

---

## Cross-cutting decisions to close before Phase 5

- [ ] Confirm **nh3 cp314 wheel** availability (else budget a Rust toolchain in the kit).
- [ ] Choose Jinja **fragment mechanism** (`jinja2-fragments` vs manual block render).
- [ ] Decide **`notes.html`: raw-HTML+nh3 vs Markdown-authored+render+nh3**.
- [ ] Decide **`html5lib` advisory kept vs dropped** once nh3 is the gate.
- [ ] Fix **CSP nonce ownership** (auth service mints; content reuses the middleware).
