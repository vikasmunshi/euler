# Secure web server — transport & infrastructure

The design of record for the `solver` web front end: a set of **isolated services**
behind a single TLS edge, delivering **server-rendered pages that feel live** (no
skeleton-page + client-fetch architecture). It is one half of a matched pair —
[access-control.md](access-control.md) covers identity and authorization; this guide
covers the transport, the service topology, and the operational build — and it holds
the authoritative **design-decision log** (DD-1…DD-9) both guides reference.
Accepted risks and regression guards are in [security-notes.md](security-notes.md).

> **Status.** Built feature-by-feature (see [Build plan](#6--build-plan)); each phase
> ships its full [maintenance kit](#51--the-maintenance-kit-per-feature-contract)
> before the next begins.
> - ✅ **Phase 1** — Caddy + ACME edge (TLS, renewal, health endpoint).
> - ✅ **Phase 2** — Squid egress (allowlist, `euler-proxy`).
> - ✅ **Phase 3** — static maintenance holding page (503 fallback + CSP).
> - ✅ **Phase 4** — Auth service (SRP login, sessions, tickets, wheel-gated admin,
>   Jinja pages, Caddy `forward_auth`); live-verified end-to-end.
> - 📐 **Phase 4a** — Authorization refinements (DD-11/DD-12: `solver/auth` RBAC kernel +
>   `authorizations.json`); **designed, not started** — a prerequisite for Phase 5.
> - ⬜ **Phases 5–6** — content service, web shell (not started).

## 1 · Purpose & scope

The front end exposes a PTY-backed `solver` shell (over a WebSocket) plus file and
command routes — arbitrary remote code execution by design. The job of this layer is
**containment and correctness of the transport**: terminate TLS at one publicly-bound
edge, isolate every app service in its own blast radius, and route the network so no
service sees traffic it should not.

**Goals**

- Every page is **composed server-side** from shared templates; the browser never
  assembles content from JSON. One template set renders both full pages and the
  fragments that update them.
- **Feels live** without a client framework or build toolchain: request-driven
  fragment swaps + server-pushed updates for long-running work.
- **Service isolation**: edge, egress, auth, content, and shell are separate
  processes with separate blast radii, wired only over loopback / unix sockets.
- **Server-side security validation** on every write path; a strict
  **Content-Security-Policy on every served page**.
- Each feature arrives with a complete **maintenance kit** — install/uninstall/
  upgrade, config generation, start/stop/status — so the system is operable at every
  step, not only when finished.

**Non-goals**

- No SPA / client-side router / client-side templating. "HTML5 app feel" is met by
  server-rendered fragment swaps, not by moving rendering to the client.
- No second language runtime. Everything stays Python + vendored browser assets; the
  PTY shell (the hardest existing code) is reused, not rewritten.
- No offline/PWA service worker in scope.

## 2 · Threat model

A home-hosted service whose login is code execution for invited collaborators (see
[security-notes.md](security-notes.md) AR-1). Three independent layers guard that
surface:

- **TLS** (Caddy) encrypts the channel and presents a browser-trusted certificate.
  It authenticates nobody — it only secures transport — and adds the transport-level
  security headers plus a fallback CSP.
- **[Authentication](access-control.md)** is the access gate: Caddy routes every
  request through the auth service's `forward_auth` endpoint before it reaches
  content or the shell, so those services never see an unauthenticated caller.
- **[Authorization](access-control.md)** (the `solver/auth` RBAC kernel +
  `authorizations.json`, DD-12) decides which commands and routes an authenticated
  identity may use.

Because login *is* RCE, the design spends its effort on **blast-radius containment**:
dedicated nologin service users (DD-2), a loopback-only app tier behind a kernel
egress firewall (DD-8), an app runtime decoupled from the repo checkout (DD-5), and
secrets scoped so no single compromise yields them all (DD-4/DD-6/DD-8).

## 3 · Design decisions

Locked, ADR-style. Each is summarised in the table, then argued below.

| Concern | Decision |
|---|---|
| TLS / edge / routing | **Caddy** (reverse proxy, `forward_auth` gate), certs via **acme.sh** DNS-01. |
| Inter-service transport | **Unix domain sockets** under `/run/euler/`, not loopback TCP — [DD-1](#dd-1--inter-service-transport--unix-domain-sockets). |
| Service identity | Dedicated nologin system users — `euler-caddy` / `euler-auth` / `euler-content` / `euler-ws` (in **`euler-web`**), plus `euler-proxy`, `euler-acme`, `euler-ddns`, `euler-smtp`. **None run as root** — [DD-2](#dd-2--service-user-strategy--dedicated-users--shared-group), [DD-4](#dd-4--no-service-runs-as-root-acme--ddns-get-dedicated-users). |
| Edge setup & lifecycle | One `scripts/setup/frontend.sh` installs **root-owned systemd units** (start/stop needs `sudo`) — [DD-3](#dd-3--edge-orchestrator--frontendsh--root-owned-systemd). |
| Egress control | **Squid** forward proxy, domain allowlist; shell/AI/scrapers reach the network only via `HTTPS_PROXY`. |
| Response headers | **Content-Security-Policy on every served page** (see [CSP](#47--content-security-policy)). |
| App framework / templating | **aiohttp + Jinja2** (autoescape on) across the app services — [DD-5](#dd-5--app-runtime--opteuler-system-venv-framework--aiohttp--jinja2). |
| App runtime | Root-owned **`/opt/euler`** system venv; services run `/opt/euler/venv/bin/python -m …`. Repo unreadable to service users — [DD-5](#dd-5--app-runtime--opteuler-system-venv-framework--aiohttp--jinja2). |
| Auth state & admin plane | State in **`/var/lib/euler-auth`** (`0600`); admin ops via a **sudo-gated admin API** — [DD-6](#dd-6--auth-state-is-euler-auth-private-admin-ops-go-through-an-admin-api). |
| Registration | **Invite-only**, two-channel: **7-day** email link → Terms → **10-min OTP** → set SRP password — [DD-7](#dd-7--registration--invite-link--terms--otp--srp-password). |
| Egress firewall | **Kernel-enforced**: systemd per-unit `IPAddressDeny` + host **nftables** owner-match; mail via a loopback `euler-smtp` relay — [DD-8](#dd-8--kernel-enforced-egress-firewall--loopback-mail-relay). |
| Identity & masquerade | Three planes — `forward_auth` headers, one-time shell ticket, checkout-owner uid — [DD-9](#dd-9--identity-authentication-and-masquerade-prevention). |
| Profiles & access | Four-rung ladder `reader`/`contributor`/`maintainer` (web) + `admin` (**local-only**); content routes gated by a resource×verb matrix; `users change` promotes/demotes — [DD-11](#dd-11--profiles--content-service-access). |
| Authorization | One `solver/auth` kernel + `authorizations.json` (RBAC) for shell **and** web; retires `commands.csv`; per-profile service instances + content-tree ACLs as the OS layer — [DD-12](#dd-12--unified-authorization-solverauth--authorizationsjson). |

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
`euler-web` can `connect()`); there is no port registry to maintain; the services have
**zero network surface** — nothing to port-scan, no `0.0.0.0` mis-bind one typo away.
Marginally lower latency helps the streaming shell WS. The one cost — socket lifecycle
— is absorbed by systemd (`RuntimeDirectory=` / tmpfiles.d) under DD-3.

**Health probes.** The health endpoint is **Caddy-native** (`respond /healthz 200`),
so it needs no socket. Per-service probes use
`curl --unix-socket /run/euler/<svc>.sock http://x/healthz`.

### DD-2 · Service-user strategy = dedicated users + shared group

**Decision.** One shared group **`euler-web`**, and a dedicated system user per app
service: **`euler-caddy`**, **`euler-auth`**, **`euler-content`**, **`euler-ws`**,
plus **`euler-proxy`** (Squid egress). Each app service's socket is `owner=euler-<svc>`,
`group=euler-web`, mode `0660`, in the `root:euler-web` runtime dir `/run/euler`. Caddy
runs as `euler-caddy` (in `euler-web`) so it can `connect()` to every upstream; its
unit grants `CAP_NET_BIND_SERVICE` to bind `:443` without root. `euler-proxy` owns no
`/run/euler` socket — Squid is reached via `HTTPS_PROXY`, not as a Caddy upstream — so
it stays outside `euler-web`.

**Why.** DD-1's isolation is only real across **distinct uids** — same-user processes
can always reach each other's sockets. Separate users give each service its own blast
radius: a compromised service cannot read another's files, signal it, or inspect its
memory, and the highest-risk `euler-ws` (RCE by design) is fully separated.

**Scope note.** A single shared `euler-web` group means any member could, in principle,
`connect()` to a peer's socket; the guards remain uid separation plus `forward_auth`
at the edge. Strict per-service socket isolation (split into `euler-auth-fe`, … each
containing only Caddy + the owner) is deferred, not needed for the phased build.

**Per-profile instances (DD-12).** The content and shell services additionally run as
**per-profile uids** — `euler-content-<profile>` / `euler-ws-<profile>`, one systemd
template-unit instance each, Caddy routing to them by `X-Profile` — so the OS layer backs
web authorization per profile, not just per service. See
[DD-12](#dd-12--unified-authorization-solverauth--authorizationsjson).

### DD-3 · Edge orchestrator = `frontend.sh` + root-owned systemd

**Decision.** A single **`scripts/setup/frontend.sh`** exposes full **`install` /
`uninstall` / `upgrade`** (plus `status` / `renew` / `reload`) for the whole edge. It:

1. creates the `euler-web` group and the `euler-*` service users (idempotent);
2. installs Caddy (apt) and acme.sh as the dedicated `euler-acme` user (DD-4);
3. issues + deploys the TLS cert via acme.sh DNS-01 into **`/etc/euler/tls`** (setgid,
   key `0640`) so `euler-caddy` reads it; the renewal hook re-applies mode + reloads;
4. generates the **`/etc/euler/Caddyfile`** unix-socket router (path →
   `unix//run/euler/*` upstreams, the `forward_auth` block, security headers +
   fallback CSP);
5. installs the **root-owned systemd *system* unit** `euler-caddy.service`
   (`WantedBy=multi-user.target`, so the edge comes up at **boot**).

**Per-concern kits.** Each other concern gets a **sibling script of the same shape** as
its phase lands — `egress.sh` (Squid), `ddns.sh` (dynamic DNS), `firewall.sh` +
`smtp.sh` (DD-8), `auth.sh` (the app tier). A `make` umbrella (`install-web`, plus
per-kit `install-frontend`, `install-egress`, …) composes them; every service stays
independently installable and restartable.

**Config location.** The edge's config and secrets live under **`/etc/euler`**, not the
repo: the dedicated `euler-caddy` user cannot traverse the repo owner's `0750` home, so
a repo-local Caddyfile/key would be unreadable. The authoring source `~/.euler/env` is
read by the installer (repo owner + sudo), which deploys scoped runtime config into
`/etc/euler`.

**Privilege model.** Because the units live in **root's** systemd and run as the
locked-down `euler-*` users, lifecycle is privileged: `start`/`stop`/`restart` require
**`sudo`**. The edge **assumes systemd** (present on dev and the deployment host).

### DD-4 · No service runs as root (acme + ddns get dedicated users)

**Decision.** No `euler-*` service runs as root. acme.sh and the DDNS updater get
dedicated nologin users, each in its own group (outside `euler-web`):

| Service | User | Code | Config | Run |
|---|---|---|---|---|
| cert issue/renew | `euler-acme` | acme.sh in `/usr/local/share/euler-acme` | caches its own state | `euler-acme.timer` (daily) |
| dynamic DNS | `euler-ddns` | `/usr/local/bin/euler-ddns` | `/etc/euler/ddns.env` (`root:euler-ddns 0640`) | `euler-ddns.timer` |

**Cert reload without root.** The reload uses **Caddy's admin API** (`caddy reload
--config /etc/euler/Caddyfile`, loopback `:2019`), not `systemctl` — so non-root
`euler-acme` triggers it. The Caddyfile is `0644` (non-secret).

**Cert deploy without chown.** `/etc/euler/tls` is `euler-acme:euler-web`, **setgid
(2750)** — acme.sh writes `server.{crt,key}` there, they inherit group `euler-web`, and
the reloadcmd `chmod`s the key `0640` so `euler-caddy` reads it via the group.

**Config source.** `~/.euler/env` is the **install-time authoring** source of truth;
the installer deploys *scoped* runtime config into `/etc/euler` (`edge.env` = FQDN +
email; `ddns.env` = FQDN + name.com creds), so no runtime service needs the repo. This
scopes secrets: `euler-ddns` sees only the name.com creds, never the full `~/.euler/env`.

### DD-5 · App runtime = `/opt/euler` system venv, framework = aiohttp + Jinja2

**Decision.** The Python app **code** runs from a **root-owned system venv at
`/opt/euler`**, *not* the repo checkout: the service users cannot traverse the repo
owner's `0750` home for *code*. The installer (`scripts/setup/auth.sh`, repo owner + sudo)
does `pip install .[web]` into `/opt/euler/venv`, and the unit runs
`ExecStart=/opt/euler/venv/bin/python -m solver.web.<svc>`. `upgrade` re-installs from
the repo. The **framework is aiohttp + Jinja2** (autoescape on) — one framework shared
with the shell service; Jinja replaces the homegrown string templating.

**Code vs. data.** This isolates the *code*; the content services still read/write the
repo's **content tree** (`solutions/`, `docs/`, `web-content/`) — the git filter leaves
plaintext at rest there, so no master key is needed. That data access is a **scoped,
per-profile ACL** on those subtrees only (never `.git`/`keys/`/`solver/`), added by
[DD-12](#dd-12--unified-authorization-solverauth--authorizationsjson) — a targeted share
with `euler-web`, not the blanket home-open this DD otherwise avoids.

**System paths.**

| Path | Owner / mode | Purpose |
|---|---|---|
| `/opt/euler/venv/` | `root:euler-web` `0755` | the deployed venv; only root writes it (install/upgrade). |
| `/run/euler/` | `root:euler-web` `0770` (tmpfiles.d) | shared socket dir; each service creates its own `*.sock` (`0660`). |

Jinja **page templates** ship as package data inside the venv
(`solver/web/templates/*.html`); **static assets** (CSS/JS) stay in the repo-root
`web-content/` tree, deployed to `/etc/euler/web-content` and served by Caddy under
`/assets/*` — so rendered pages reference `'self'` assets and the CSP holds.

### DD-6 · Auth state is `euler-auth`-private; admin ops go through an admin API

**Decision.** All auth state is owned by **`euler-auth` alone** (`0600`, under the
unit's `StateDirectory=/var/lib/euler-auth`); no file is shared with the repo owner.
The admin shell commands never touch those files — they call an **admin API on the auth
service**. Full state schema and the admin plane are in
[access-control.md](access-control.md); the security-relevant shape:

| Path | Owner / mode | Purpose |
|---|---|---|
| `/var/lib/euler-auth/*.json`, `session-secret` | `euler-auth:euler-auth` `0600` | verifier DB, pending invites, remember-me, HMAC secret. |
| `/etc/euler/auth.env` | `root:euler-auth` `0640` | scoped runtime config; deployed from `~/.euler/env` (DD-4). Holds the root-only `EULER_ADMIN_TOKEN`. |

**Admin plane (wheel-gated).** The admin API is **local-only** — a dedicated listener
(`/run/euler-adm/auth-admin.sock`, `0600` `euler-auth`-private), **never routed through
Caddy**. Only **root** can connect: the `users` command re-executes the admin CLI under
`sudo`, so every admin action passes sudo's password gate and audit trail. The
`X-Admin-Token` lives **only** in root-readable `auth.env`. Rationale: the operator is a
sudoer, and the operator's ordinary uid is the most *exposed* on the host (browsers,
dev tooling, AI agents) — a bespoke admin group + operator-readable token would let any
process running as the operator silently mint admin invites, gating the highest-privilege
API *below* sudo.

**Why an API over shared files.** Keeps auth state single-writer and `0600`, so no other
uid can corrupt or read the verifier DB; the service owns all invariants.

### DD-7 · Registration = invite link → Terms → OTP → SRP password

**Decision.** Registration is **invite-only and two-channel**: an admin mints an invite;
the invitee proves live mailbox control (OTP) and accepts Terms before a password is
set. All secrets are stored hashed; every step is single-use and time-boxed. The same
link→OTP→password pipeline serves self-service password **reset** (skipping Terms);
admins never reset passwords. The full flow, state machine, and parameters (7-day link,
6-digit/10-min/5-try OTP, scroll-gated Terms) are in
[access-control.md § 4.1](access-control.md).

### DD-8 · Kernel-enforced egress firewall + loopback mail relay

**Decision.** "Egress only via Squid" is enforced at the **kernel**, not just by the
`HTTPS_PROXY` env var (which a compromised process can ignore). Two layers:

1. **systemd per-unit IP filter** — every loopback-only app unit (`euler-auth`,
   `euler-content`, `euler-ws`) carries `IPAddressDeny=any` + `IPAddressAllow=localhost`,
   so the app tier reaches **only loopback** (their `/run/euler` sockets, the Squid
   proxy at `127.0.0.1:3128`, and the loopback mail relay). `euler-caddy` is the
   exception — it terminates public inbound `:443`, which the (bidirectional) systemd
   filter would block; its egress lock comes from layer 2: `ct state
   established,related` permits its replies while any *NEW* outbound it initiates hits
   the drop.
2. **host nftables owner-match** (`scripts/setup/firewall.sh` → `euler-firewall.service`,
   `/etc/euler/nftables.conf`) — a `table inet euler` with an **egress-only**
   (`hook output`) chain, scoped to the `euler-*` uids, permitting loopback and only the
   specific `(uid, port)` each service needs, then dropping the rest:

   | uid | allowed egress |
   |---|---|
   | `euler-proxy` (Squid) | `tcp dport {80,443}` — the **only** service with real internet; its L7 allowlist still applies |
   | `euler-acme` | `tcp dport 443` (ACME + DNS-provider API) |
   | `euler-ddns` | `tcp dport 443` (name.com API, ipify) |
   | `euler-smtp` (relay) | `tcp dport 587` (Gmail submission) |
   | infra uids | `udp/tcp dport 53` (DNS, unless the resolver is on loopback) |
   | all `euler-*` | loopback; **everything else dropped** |

   The chain uses `policy accept` and drops **only** the enumerated `euler-*` uids (a
   final `skuid { … } drop`), so non-service traffic — SSH, root, your shell — is
   untouched (no lock-out risk). **Loopback is matched by destination address** (`ip
   daddr 127.0.0.0/8` / `ip6 daddr ::1`), not `oif "lo"`: the interface-index match does
   not hit loopback output on the WSL2 kernel (observed on
   `6.6.114.1-microsoft-standard` — euler uids' loopback SYNs fell through to the final
   drop while replies still passed via `ct state established`, so only *new*
   service-to-service connects broke), and the address space is the actual security
   intent. Host `INPUT` policy is left alone (inbound `:443` is Caddy's; SSH stays
   reachable).

**Mail relay (`euler-smtp`).** So the app tier needs **no** direct-internet exception,
OTP/invite mail goes through a small **loopback submission relay** (dedicated
`euler-smtp` user, own group): it listens on `127.0.0.1:8025`, is the **sole holder of
the Gmail credentials** and the **sole uid permitted `:587`**, **forces the envelope
sender** to `SMTP_ADDRESS`, and never logs bodies (they carry OTPs). A firewall relay
guard bars every other euler-* uid from `:8025`. `euler-auth` submits via loopback SMTP
with no credentials of its own. Relay config (`/etc/euler/smtp.env`, `root:euler-smtp
0640`) is deployed from `~/.euler/env`.

**Why.** Without this, "plaintext must never leave the repo" and the Squid allowlist
rest on an environment variable. The firewall makes Squid the *only* internet path for
the app tier at the packet level; the relay keeps the SMTP exception off the app uids
and the Gmail password out of every service but one.

### DD-9 · Identity, authentication, and masquerade prevention

**Decision.** The auth service is built **fresh** as `solver/web/auth`; identity
resolution (`solver/utils/identity.py`) is redesigned around **three planes**, each with
an explicit voucher — web request (`forward_auth` → `X-User`/`X-Profile`), web shell
(one-time ticket redeemed over `auth.sock`), local terminal (checkout-owner uid →
`admin`, a real non-owner login → `contributor`, a `euler-*` service uid without a ticket
→ abort; see [DD-11](#dd-11--profiles--content-service-access)). `SOLVER_USER` is
display-only; there is no anonymous fallback. The full
mechanism (the shell ticket, the masquerade vector→guard table, the resolution order)
lives in [access-control.md § 4.5](access-control.md) and its
[threat model](access-control.md#2--threat-model); the transport-side guarantee is that
**Caddy strips client-supplied `X-User`/`X-Profile`** and forwards only the
`forward_auth` response headers, and that app sockets are reachable only via Caddy
(DD-1/DD-2).

### DD-10 · Phase-5 content-service choices

**Decision.** The four choices flagged for the content service, resolved before its
build (see [Build plan → Phase 5](#phase-5--content-service-)):

- **HTML sanitisation = nh3, sanitize-and-store-clean.** Adopt **nh3** as the
  save-time gate for `.html` solution files. The `cp38-abi3-manylinux_2_17_x86_64`
  stable-ABI wheel installs and imports on this project's Python 3.14 — **no Rust
  toolchain** — so it is pinned in the `web` extra with a kit `check` that verifies the
  import. On save, nh3 runs a tailored allowlist (`article/h3/h4/p/ul/li/table/code/a`,
  keeping `a`'s `class/target/rel/href`; MathJax `$…$` survives as text) and the
  **sanitised output is stored** — like the JSON-reindent path, and the editor shows the
  diff. *Store-clean, not reject-and-restore:* nh3 always normalises (adds `<tbody>`,
  rewrites `rel`), so reject-and-restore would bounce essentially every save. nh3 gates
  what is *stored*; the CSP (§4.7) blocks what would *execute* — independent layers.

- **Fragment mechanism = a manual named-block render helper.** htmx fragments render a
  named `{% block %}` of the same template via Jinja's own API
  (`tmpl.blocks[name](tmpl.new_context(ctx))`), wrapped in a ~5-line async-safe helper in
  `solver/web/`. Verified on Jinja2 3.1.6. **No new dependency** — `jinja2-fragments`
  would add a pinned dep that is mostly Flask/Quart glue for the same few lines.

- **`notes.html` stays raw HTML (+ nh3), not Markdown.** Notes are semantic HTML5 — as
  the AI convention (`convention_documentation.md`) and the entire existing corpus
  already are — with math as MathJax TeX **text** (`$…$`, never `<script>`/MathML). nh3
  simply closes the stored-XSS hole; there is no hand-authored-raw-HTML hazard for
  Markdown to remove. A Markdown switch would mean rewriting the convention, re-adding
  `markdown-it-py`, retraining the AI skill's emit format, and migrating the corpus —
  churn with no safety gain.

- **`html5lib` dropped.** With nh3 as the enforcing gate, its sanitised-vs-original diff
  is the author's feedback in the editor; a second HTML parser for advisory
  well-formedness is not worth the extra dependency. `html5lib` stays out of the `web`
  extra (where Phase 4 already dropped it).

### DD-11 · Profiles & content-service access

**Decision.** Authorization runs on a **four-rung profile ladder**, re-columning
`commands.csv` (was `admin`/`user`/`guest`). The headline: **`admin` is local-only** —
the top *web* tier is `maintainer`, so **no web account can reach the infra commands**
(`git-*`, `key-*`, `users`, `manage-config`) or the crypto master key. The lowest tier,
`reader`, is a **stepping stone**: a new invitee starts read-only and is promoted as
trust grows.

| Profile | Reached by | Gains over the rung below |
|---|---|---|
| **reader** | web invite (default) | **view** only — framework docs, the full solution tree (public **and** decrypted private), static assets |
| **contributor** | web (promoted), or a local non-owner login | + **edit** solution files (code / notes / tests) + **execute** (eval / benchmark, and the Phase-6 web shell) |
| **maintainer** | web (promoted) | + **delete** solution files + the AI commands (`claude-api` / `claude-skill`, which spend the owner's API budget) |
| **admin** | **local terminal only** (uid == repo-owner) | + infra: `git-*`, `key-*`, `users`, `manage-config`, `update-*`. **Never web-assignable.** |

Read scope is **uniform** — every authenticated account, `reader` included, may read the
decrypted `solutions/private` plaintext (the [AR-2](security-notes.md) posture; the
invite list is the trust boundary).

**Content-service access matrix.** Route guards map to `commands.csv` capabilities — one
policy across shell and web (the DD-6 invariant) — with a `view` capability added for
pure-GET pages:

| Verb | Routes | reader | contributor | maintainer | admin |
|---|---|:---:|:---:|:---:|:---:|
| view | GET summary / problem / code / docs; file reads | ✓ | ✓ | ✓ | ✓ |
| edit | save a solution file (incl. `notes.html`, + nh3, DD-10) | | ✓ | ✓ | ✓ |
| delete | delete a solution file | | | ✓ | ✓ |
| execute | eval / benchmark; the Phase-6 web PTY shell | | ✓ | ✓ | ✓ |

Static `web-content` assets are Caddy-served and never writable through the service.
`execute` at `contributor`+ keeps the Project-Euler workflow intact (a contributor runs
the solution they wrote) while making `reader` genuinely RCE-free
([AR-1](security-notes.md)); the web PTY shell (Phase 6) is likewise `contributor`+, so
`reader` gets no terminal. The *mechanism* that enforces this matrix — the RBAC kernel,
`authorizations.json`, and the per-profile OS layer — is
[DD-12](#dd-12--unified-authorization-solverauth--authorizationsjson) (which retires
`commands.csv` and moves the profile off the SRP user record).

**Identity resolution (refines DD-9).** The local-terminal plane now yields *two*
profiles, but service uids must not escalate:

1. `SOLVER_TICKET` set → redeem over `auth.sock` → the account's stored profile; failure
   aborts.
2. else uid == repo-owner → **admin**.
3. else a **`euler-*` service account** (no ticket) → **abort** — this blocks a `reader`
   web shell from re-execing `solver` as `euler-ws` (after `unset SOLVER_TICKET`) to gain
   `contributor`.
4. else a real non-owner login → **contributor**.
5. else abort.

**`users change`.** Promotion/demotion is a first-class admin verb —
`users change <email> <profile>` (profile ∈ `reader`/`contributor`/`maintainer`; `admin`
is not web-assignable) on the sudo-gated admin plane. Like `disable`, it **revokes the
account's live sessions and remember tokens**: the profile is baked into the session at
login and into the shell at ticket-redeem, so a change takes effect on next login.

### DD-12 · Unified authorization (`solver/auth` + `authorizations.json`)

**Decision.** One authorization kernel — the **`solver/auth`** sub-package — serves both
the shell and the web from one policy file, **`authorizations.json`**. It supersedes the
per-command `commands.csv` (retired) and the profile field on the SRP user record
(DD-6/DD-11), which were shell-only and web-only respectively and did not compose.
Enforcement is layered: the command decorator (shell) and the app router (web) are the
primary check; a per-profile **OS-ACL** layer backs it on the filesystem (DD-2/DD-5
extensions below). Roles→permissions→objects is classic RBAC, expressive enough for the
web content service's path-scoped read/write/execute.

**The kernel & the subject.** `solver/auth` owns identity resolution (absorbing
`solver/utils/identity.py`), the profile ladder, and the permission model. It resolves a
single **subject** once per process:

```
Subject(user, channel, auth_method, profile, permissions)
```

`channel ∈ {terminal, web}`; `auth_method` records *how* identity was proven (checkout-uid,
shell-ticket, SRP-session); `permissions` is the inheritance-expanded grant set. The web
*authentication* service (`solver/web/auth`: SRP, sessions, tickets, registration) stays
separate and **imports `solver/auth`** to turn an authenticated email into a subject —
authN and authZ are distinct packages.

**`authorizations.json`** is the **system of record, outside the repo** —
`/etc/euler/authorizations.json`, `root`-owned (`0644`: world-readable non-secret policy,
**root-write only**). It is *not* a repo file: a repo write cannot change policy, and every
mutation goes through the **sudo-gated `users` path** (DD-6). The repo ships only a
bootstrap template; the installer seeds the real file (including the **checkout owner as
`admin`**, below). Both the local shell and the services read it.

```json
{
  "profiles": {
    "reader":      { "inherits": null,          "grants": ["solver:execute","solutions:read","docs:read","web-content:read","users:read"] },
    "contributor": { "inherits": "reader",      "grants": ["solutions:write","solutions:execute"] },
    "maintainer":  { "inherits": "contributor", "grants": ["solutions:delete","ai:execute"] },
    "admin":       { "inherits": "maintainer",  "grants": ["shell:execute","infra:execute","users:write"] }
  },
  "users":   { "vikas": "admin", "vikas.munshi@gmail.com": "maintainer", "mercanther@gmail.com": "reader" },
  "objects": { "solutions": ["solutions/"], "docs": ["docs/"], "web-content": ["web-content/"],
               "solver": [], "shell": ["/bin/bash"], "ai": [], "users": [], "infra": [] }
}
```

- **users** — keyed by **web email _or_ os-login name** (so it scales to both channels).
  `"vikas": "admin"` is the checkout owner, seeded at install. The web channel is capped at
  `maintainer` (a `users` entry granting `admin` is never honoured over the web).
- **`users` is itself an object**: `users:read` (roster listing) is a `reader` grant;
  `users:write` (add / change / enable / disable / remove) is `admin` only. This needs the
  kernel to answer **runtime** permission queries (`subject.has('users:write')`), not just
  the registration-time gate — so one `users` command serves a read path to `reader`+ and
  gates its mutating verbs to `admin`.

- **profiles** — each a set of `object:permission` grants (`permission ∈ read/write/
  execute/delete`), with single-parent `inherits` so grants stay DRY (the DD-11 ladder,
  exactly).
- **users** — identity→profile for **web emails** and, optionally, named local logins.
  The **checkout owner is `admin` by the uid anchor** (DD-11 §resolution) and need not be
  listed; the **web channel is capped at `maintainer`** (a `users` entry granting `admin`
  is never honoured over the web).
- **objects** — the permission namespace, each mapped to zero or more filesystem paths.
  Path-bearing objects (`solutions`/`docs`/`web-content`) drive the OS-ACL layer; the
  path-less ones (`solver`/`shell`/`ai`/`infra`) are pure capabilities checked in-app.

**The decorator (policy-*requirement* point).** `@register`/`@command` gain two lists:
`requires=[...]` (the `object:permission`s the command needs) and `channels=(...)`
(default both). Enforcement, at registration: the command is registered only if
`channel ∈ channels` **and** `requires ⊆ subject.permissions`; otherwise it is invisible
(unknown-command / not-registered), exactly as today. A command with **no `requires`
defaults fail-closed** to `infra:execute` (admin-only) — a new command is never silently
exposed. Example mapping: `show → solutions:read`; `new`/`edit` → `solutions:write`;
`evaluate`/`benchmark` → `solutions:execute`; `!` → `shell:execute`; `claude-*` →
`ai:execute`; `git-*`/`key-*`/`manage-config` → `infra:execute`; `users` splits by verb
(`list → users:read`, mutations → `users:write`). A generated **`solver/commands.json`**
(by `update-docs`) reports each command's `requires`/`channels` for audit — the generated
audit view, distinct from the authored `authorizations.json`.

**`modules.csv` → loader-only.** It keeps just `(module, registers_commands)`; the
`terminal`/`web` columns are gone (channel now lives on the decorator, finer-grained). All
modules import; wrong-channel commands simply don't register.

**Enforcement points.**

| Surface | Primary check | Second layer |
|---|---|---|
| Shell (terminal + web PTY) | the command decorator (`requires ⊆ perms`, `channel`) | the per-profile uid's filesystem ACLs |
| Web routes (content service) | app-router `requires(<capability>)` on `X-Profile` | the per-profile instance's uid + ACLs |

**OS second layer — per-profile instances (extends DD-2).** All web users share one uid,
so the filesystem cannot tell a `reader` request from a `contributor` one *within* a single
service process. To make the OS layer real per-profile, the web app services run as
**per-profile instances** — systemd **template units** `euler-content@<profile>.service` /
`euler-ws@<profile>.service`, each `User=euler-content-<profile>` on its own socket — and
**Caddy routes by the `X-Profile`** that `forward_auth` returns to the matching upstream
(`unix//run/euler/content-<profile>.sock`). No process changes uid (no root, no setuid);
each instance is *born* as the right uid. A shell's redeemed-ticket profile must match its
instance's uid, else it aborts.

**OS second layer — content-tree ACLs (refines DD-5).** The services read/write the repo
**working tree directly** (`solutions/`, `docs/`, `web-content/`) — the git clean/smudge
filter already leaves **plaintext at rest** there, so the web tier needs *filesystem
access, not the master key*, and does **no git operations** (commit/checkout, where the key
is used, stay with the operator locally). Access is a **scoped ACL**: a traverse ACL
(`g:euler-web:x`) on the home path + repo root so services can *reach* the content subtrees
without reading the rest of home, then per-profile group ACLs — `euler-sol-read` (traverse
+ read `solutions/`), `euler-sol-write` (write), `euler-sol-delete` — mapped to the
per-profile uids. **`.git`, `keys/` (the `enc-key.json`), and the `solver/` source are
never in the ACL set.** `authorizations.json`'s `objects`→paths is the single source that a
setup kit turns into these ACLs, so the app policy and the filesystem enforcement can't
drift. This *refines* DD-5 (which kept the whole repo unreadable to service users): the
venv still lives in `/opt/euler` for code isolation, but the **content tree** is
ACL-shared with `euler-web`, per-profile — a targeted share, not the blanket home-open
DD-5 rejected. The master key never reaches the services; a web compromise reads
working-tree plaintext (accepted, [AR-2](security-notes.md)) but cannot obtain the key.

**Profile resolution (`solver/auth`, replacing `utils/identity.py`).** The profile is the
`users` map's value for the resolved identity — one source for both channels:
1. **web** (channel=web): `profile = users.get(email)`, **capped at `maintainer`**.
2. **local terminal**: a `euler-*` service uid without a ticket → abort; else
   `users.get(os_login)`; else — if not in the map and the uid **owns the checkout** →
   `admin` (an un-lock-out-able floor; the installer also seeds the owner explicitly, so an
   explicit map entry wins and lets the operator run local at a lower profile deliberately);
   else `contributor`.

**Two-path `users add`.** `users add <email>` is the web path (mint an invite → registration
→ the account's profile entry); `users add <os-login>` is the local path — a bare username
gets a direct `users`-map entry, no invite (a local login authenticates by *being* that OS
user). Both write the sudo-gated `/etc/euler/authorizations.json`.

**Staleness = re-login.** The subject resolves its permissions once at process start, so an
`authorizations.json` edit takes effect on the next login / shell-start; `users change`
already revokes sessions to force it. Consistent with DD-11.

### Open decisions

All resolved:

- ~~**Framework/templating**~~ → aiohttp + Jinja2 (DD-5).
- ~~**CSP nonce ownership**~~ → shared `solver/web/csp.py` middleware mints a
  per-response nonce; every rendering service applies it.
- ~~**htmx** for liveness~~ → adopt ([§4.6](#46--liveness--htmx)).
- ~~**nh3 / fragments / notes format / html5lib**~~ → the Phase-5 content-service
  choices, [DD-10](#dd-10--phase-5-content-service-choices).

## 4 · How it works

### 4.1 Target topology

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

Every app service binds a **unix domain socket** under `/run/euler/`; **only Caddy is
publicly bound**. Caddy authenticates every request through `forward_auth` before it
reaches content or shell, so those services never see an unauthenticated caller even
with a bug.

### 4.2 The edge (Caddy + acme.sh DNS-01)

```
Internet / LAN
   │  https :443
   ▼  Router: forward TCP 443 → <host LAN ip>:443   ·   Firewall: inbound allow 443
   ▼
   Caddy :443   ── runs as euler-caddy, config /etc/euler/Caddyfile ──
      │  terminates TLS (loads /etc/euler/tls/server.{crt,key})
      │  strips client X-User/X-Profile; security headers; forward_auth gate
      ├─►  unix //run/euler/auth.sock       (euler-auth)      — Phase 4
      ├─►  unix //run/euler/content.sock    (euler-content)   — Phase 5
      └─►  unix //run/euler/ws.sock         (euler-ws)        — Phase 6
   ▲
 acme.sh (euler-acme, /usr/local/share/euler-acme)
   └─  DNS-01 ─► name.com API (writes _acme-challenge TXT) ─► Let's Encrypt
       reloadcmd: fix key mode + `caddy reload` (admin API — no root)
 euler-ddns ─► name.com API (keeps the euler A record → current public IP)
```

No app service binds a TCP port — Caddy reaches each over a **unix domain socket**
(DD-1), and only Caddy on `:443` is network-exposed. DNS-01 needs no inbound port, so
nothing listens on `:80` (`auto_https disable_redirects`).

**Why acme.sh rather than Caddy's own ACME:** the `caddy-dns/namedotcom` plugin is
unmaintained and no longer builds against current Caddy. Issuance is delegated to
**acme.sh** (whose `dns_namecom` client speaks the name.com API); stock Caddy simply
loads the resulting certificate by absolute path. This keeps the DNS-01 benefit — a real
certificate with no inbound port open — without a broken plugin.

**The DNS API token** drives two things, both outside Caddy: the **DNS-01 challenge**
(acme.sh writes `_acme-challenge.<FQDN>` TXT at issue/renewal) and **dynamic DNS**
(`ddns.sh` keeps the `<FQDN>` A record on the current public IP, public access only).
Both use the same name.com token; acme.sh caches it for renewals.

**The Caddyfile** (generated to `/etc/euler/Caddyfile`, `0644`): Caddy loads the acme.sh
cert by absolute path and performs no ACME of its own. It strips client
`X-User`/`X-Profile` (DD-9), serves `/healthz` (Caddy-native) and `/assets/*` (static),
routes the public auth surface (`/login`, `/register*`, `/reset*`, `/forgot`, `/terms`,
`/auth/*`) to `unix//run/euler/auth.sock`, and gates everything else through
`forward_auth` (`/auth/check` → `200` + `X-User`/`X-Profile` copied onto the request, or
`401` → `302 /login`), falling through to the maintenance holding page until the content
service lands. Regenerate + validate with `frontend.sh upgrade` and `sudo caddy validate
--config /etc/euler/Caddyfile`.

**The service.** `euler-caddy.service` is a **root-owned** system unit, boot-enabled,
running Caddy as unprivileged `euler-caddy`: `AmbientCapabilities=CAP_NET_BIND_SERVICE`
to bind `:443`, `RuntimeDirectory`/tmpfiles for `/run/euler`, and the hardening set
(`NoNewPrivileges`, `ProtectHome`, `ProtectSystem`, `PrivateTmp`). Lifecycle needs
`sudo` (DD-3).

### 4.3 Egress (Squid)

A Squid forward proxy on loopback `127.0.0.1:3128` with a **domain allowlist**
(`api.anthropic.com`, `.projecteuler.net`, `.github.com`, `.githubusercontent.com`;
default-deny), running as the dedicated `euler-proxy` user outside `euler-web`. The
client-side `HTTPS_PROXY`/`HTTP_PROXY` is written to `/etc/euler/egress.env`, loaded by
the app-service units via `EnvironmentFile=`, so AI features, the problem scraper, and
`gh` egress only through Squid — operationalising "plaintext must never leave the repo"
at the network layer. Config in `/etc/euler-proxy` (`squid.conf` + editable
`squid.allowlist`). The kernel firewall (DD-8) makes Squid the *only* internet path at
the packet level, so the allowlist cannot be bypassed by ignoring the env var.

### 4.4 App runtime

The Python services run from the root-owned `/opt/euler` venv (DD-5), never the repo.
`scripts/setup/auth.sh` provisions the `euler-auth` identity, builds the venv (`pip
install .[web]`), deploys the scoped `/etc/euler/auth.env`, provisions
`/var/lib/euler-auth` and the runtime socket dirs, and installs the root-owned
`euler-auth.service` (carrying the DD-8 `IPAddressDeny` filter). Content and shell
services follow the same shape in Phases 5–6.

### 4.5 Framework / templating

aiohttp stays the one framework across content + shell; **Jinja2** (via
`aiohttp-jinja2`, autoescape on) replaces the homegrown `template.replace(...)` +
manual `html.escape` string engine (no inheritance, no partials, no autoescaping — an
XSS footgun). FastAPI was considered and rejected: its headline value (pydantic JSON +
OpenAPI) is for JSON APIs, precisely what this SSR design moves away from, and it adds
starlette + pydantic + uvicorn weight beside the aiohttp shell service.

Rendering contract:

- `base.html` owns `<head>` (shared CSS, vendored JS), the header/nav include, and the
  footer. Every page `{% extends "base.html" %}`.
- Autoescape **on**. Any pre-sanitised HTML is injected through an explicit `| safe`
  only after passing [nh3](#47--content-security-policy--nh3).
- A route renders either the **whole page** or a **named block/fragment** of the same
  template — via a manual block-render helper ([DD-10](#dd-10--phase-5-content-service-choices))
  — so a full load and a live update share one source of truth.

### 4.6 Liveness · htmx

"Feels live" has two regimes, both keeping the server as the sole renderer:

1. **Request-driven** (edit → save → validation panel; navigate a file list; quick
   eval) → **htmx**: `hx-get`/`hx-post` fetch a rendered HTML fragment (a Jinja block)
   and swap it in. No client JSON, no client templating.
2. **Server-pushed** (benchmark progress, long output) → **SSE** (htmx SSE extension)
   or the existing shell WebSocket. Prefer SSE for one-way content-service progress;
   reserve the WS for the interactive shell.

htmx is ~14 kB, vendored into `web-content/vendor/` (pinned + SRI + `LICENSES`) exactly
like xterm.js/codemirror. It **strengthens** the CSP/XSS story: no client-side
string→DOM assembly (no DOM-XSS class), all escaping is Jinja autoescape server-side.
**CSP interaction (must design for):** with `script-src 'self'` and no `unsafe-inline`,
use `hx-*` attributes (fine — not inline script) and **avoid `hx-on:` handlers**; set
`htmx.config.includeIndicatorStyles = false` and ship the indicator CSS in the bundle so
`style-src 'self'` needs no `unsafe-inline`. **Verdict: adopt** (Phase 5).

### 4.7 Content-Security-Policy · nh3

**CSP — locked: every served page carries one.** It is emitted by an **app middleware**
(`solver/web/csp.py`, shared by every rendering service), because a strict policy uses a
**per-response nonce** for any unavoidable inline `<script>`/`<style>`; the app that
renders the page mints the nonce and stamps it into both the header and the template.
Baseline: `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'
data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'`
— no `unsafe-inline`, no `unsafe-eval`. **Caddy** adds the transport-level headers that
need no per-response state (HSTS, `X-Content-Type-Options`, `Referrer-Policy`) and a
fallback CSP for purely static responses. Vendored JS (htmx, xterm, codemirror, MathJax)
is served from `'self'`.

**nh3 (Phase 5 save gate).** The edit path validates `.py` (flake8 + autofix), `.c`
(compile), and `.json` (parse/reserialise) with reject-and-restore, but writing `.html`
verbatim would be a **stored-XSS hole** (`notes.html` is served back and rendered).
**nh3** (the Rust/Ammonia sanitiser, maintained successor to `bleach`) closes it with an
allowlist on save — strip `<script>`, `on*` handlers, `javascript:`/`data:` URLs,
unknown tags/attrs — running **sanitize-and-store-clean** (nh3 normalises, so
reject-and-restore would bounce every save). Defence in depth with the CSP (nh3 gates
what is *stored*, CSP blocks what would *execute*). The Phase-5 caveats are settled in
[DD-10](#dd-10--phase-5-content-service-choices): the `cp38-abi3` wheel installs on 3.14
(no Rust toolchain); the allowlist is tuned for `notes.html`'s HTML5 tag set with MathJax
TeX surviving as text; notes stay raw-HTML (not Markdown); and the advisory `html5lib`
check is dropped in favour of nh3's own diff. **Verdict: adopt** as the save gate.

## 5 · Operating it

### 5.1 The maintenance-kit (per-feature contract)

Every phase ships **all** of these before it is "done":

1. **Design note** — a section here or a dedicated `docs/*.md`, cross-linked.
2. **Dependency management** — `install`/`uninstall`/`update` for the feature's deps:
   Python deps pinned in a `pyproject` optional group + an importability/wheel check;
   vendored browser assets via a pinned + SRI + `LICENSES` vendoring script; system deps
   (caddy, squid, nftables) via the idempotent kit.
3. **Configuration** — a generator for host-specific config, written to `/etc/euler`
   (readable by the service users) or gitignored in-repo, from the single-source
   `~/.euler/env` (e.g. the FQDN `EULER_TLS_DOMAIN`).
4. **Lifecycle** — `start`/`stop`/`status`/`restart` via a **root-owned systemd system
   unit per service** (boot-enabled), so lifecycle needs `sudo` (DD-3).
5. **Health probe** — a `status` that reports actually-serving (HTTP/socket ping), not
   just "process exists".

An **umbrella** (`make install-web` / `uninstall-web` / `upgrade-web`) composes the
per-service kits so the whole stack installs/removes/upgrades as one, while each service
remains independently operable.

### 5.2 Install the stack

Set the deployment FQDN once in the authoring env file, then bring up the whole stack:

```bash
echo 'EULER_TLS_DOMAIN=euler.vikasmunshi.com' >> ~/.euler/env   # if not already set
make install-web        # frontend → egress → ddns → firewall → smtp → auth (sudo)
# or per kit: make install-frontend | install-egress | install-firewall | install-smtp | install-auth
```

`~/.euler/env` also carries the DNS provider's credential pair (default
`NAMEDOTCOM_USERNAME` / `NAMEDOTCOM_TOKEN`), the Gmail relay creds (`SMTP_ADDRESS`,
`SMTP_APP_PASSWORD`), and `ANTHROPIC_API_KEY`. The DNS provider is selectable via
`$EULER_TLS_DNS_PROVIDER` (default `namecom`; also `cloudflare`, `route53`, `godaddy`,
`digitalocean`, `gandi`) — each maps to an acme.sh hook and its credential pair.

Lifecycle is privileged (DD-3): `sudo systemctl restart euler-<svc>`, or the kit's own
`status`/`reload`/`renew`. Register the first admin account with `users add` (see
[access-control § 6](access-control.md)).

### 5.3 Going public (router + firewall + DDNS)

Needed only for access beyond the LAN; [access-control.md](access-control.md) is what
makes that access safe.

- **Router:** port-forward **TCP 443 → the host's LAN IP** (no port 80 for DNS-01), and
  give the host a **DHCP reservation** so its LAN IP does not drift.
- **System firewall (WSL2 mirrored mode → Windows Hyper-V Firewall):** from an elevated
  PowerShell —

  ```powershell
  New-NetFirewallHyperVRule -Name "WSL-Caddy-443" -DisplayName "WSL Caddy HTTPS" `
    -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' `
    -Protocol TCP -LocalPorts 443 -Action Allow
  ```

  Confirm the VMCreatorId with `Get-NetFirewallHyperVVMCreator`; requires `[wsl2]
  firewall=true` in `.wslconfig` (the default).
- **Dynamic DNS:** `scripts/setup/ddns.sh install` runs `euler-ddns.timer` (every 5 min,
  as `euler-ddns`), PUTting the name.com A record only when the public IP
  (`api.ipify.org`) changes, using the **same name.com token as DNS-01**. Being infra
  egress, it does **not** pass through Squid.

### 5.4 Renewal & lifecycle

- **acme.sh** runs as non-root `euler-acme` on `euler-acme.timer` (daily, `acme.sh
  --cron`); its `--reloadcmd` fixes the key mode and reloads via Caddy's **admin API** —
  no `systemctl`, no root. Renewal needs no DNS credentials re-supplied: acme.sh saves
  the token in the cert `.conf` at issue time. Force one with `frontend.sh renew`.
- **status** across the stack: each kit's `status` reports unit + health; `frontend.sh
  status` shows cert expiry and `/healthz`.

### 5.5 Configuration summary

| Layer | Key config |
|---|---|
| Authoring source | `~/.euler/env`: `EULER_TLS_DOMAIN`, DNS creds, `SMTP_ADDRESS`/`SMTP_APP_PASSWORD`, `ANTHROPIC_API_KEY` (repo owner reads; installer deploys scoped copies) |
| Edge | `/etc/euler/Caddyfile` (`0644`), `/etc/euler/tls/server.{crt,key}` (setgid, key `0640`), `/etc/euler/web-content` |
| Egress | `/etc/euler-proxy/{squid.conf,squid.allowlist}`; client `HTTPS_PROXY` in `/etc/euler/egress.env` |
| Firewall + relay | `/etc/euler/nftables.conf`; `/etc/euler/smtp.env` (`root:euler-smtp 0640`) |
| App tier | `/opt/euler/venv`; `/etc/euler/auth.env` (`root:euler-auth 0640`); `/var/lib/euler-auth` (`0600`) |
| Sockets | `/run/euler/*.sock` (`0660 euler-<svc>:euler-web`); `/run/euler-adm/auth-admin.sock` (`0600`) |

## 6 · Build plan

Built strictly in order; each phase is independently runnable and shipped with its full
[maintenance kit](#51--the-maintenance-kit-per-feature-contract). The stack is useful
and demonstrable at the end of every phase.

### Phase 1 — Caddy + ACME (edge) ✅
Public `:443` edge terminating TLS with an auto-renewing cert, a Caddy-native `/healthz`,
security headers + fallback CSP. Built as `scripts/setup/frontend.sh`: the `euler-web`
group + `euler-caddy`/`euler-acme` users, Caddy + acme.sh (DNS-01), the cert to
`/etc/euler/tls`, the generated Caddyfile, and the root-owned `euler-caddy.service`.

### Phase 2 — Squid (egress) ✅
`scripts/setup/egress.sh`: Squid on loopback `127.0.0.1:3128` with a domain allowlist
(default-deny), as `euler-proxy`; `HTTPS_PROXY` wired to the app units via
`/etc/euler/egress.env`. `status` probes an allowed and a denied domain.

### Phase 3 — Maintenance page (static) ✅
Folded into `frontend.sh`: a single static "under maintenance" page served end-to-end —
proves TLS, routing, headers, and CSP fallback on a real response. Establishes the
`web-content/` static layout and the CSP baseline the app services inherit; a
`handle_errors` block reuses it whenever a later upstream is down.

### Phase 4 — Auth service ✅
The full access layer, live-verified end-to-end (invite → scroll-gated Terms → OTP →
browser-derived SRP verifier → login, across the profile tiers). Design and mechanism in
[access-control.md](access-control.md); infrastructure in DD-5 (runtime), DD-6 (state +
admin plane), DD-8 (firewall + relay). Delivered in five steps:

1. **`firewall.sh` + `smtp.sh` kits (DD-8)** — the per-uid nftables egress ruleset and
   the loopback mail relay, so the app tier is loopback-only from its first deploy.
2. **`web` extra + `/opt/euler` deploy (DD-5)** — the `web` optional group
   (`aiohttp`/`aiohttp-jinja2`/`jinja2`); `auth.sh` provisions `euler-auth`, the venv,
   the scoped `auth.env` (root-only `EULER_ADMIN_TOKEN`), state, and socket dirs.
3. **Fresh `solver/web/auth` + admin API (DD-6, DD-9)** — stores on `/var/lib/euler-auth`,
   sessions, one-time shell tickets, the wheel-gated admin API + `users` command, and the
   DD-9 `identity.py` redesign. Verified by a 31-check harness.
4. **Jinja pages + CSP-nonce middleware (DD-7)** — `solver/web/csp.py`, the login /
   register / reset / forgot / terms pages, and the browser SRP client (byte-for-byte
   interop-tested under Node). Verified by a 27-check flow harness.
5. **Activate Caddy `forward_auth`** — strip client identity headers, route the public
   auth surface, gate everything else; falls through to the maintenance page until
   content lands.

### Phase 4a — Authorization refinements ⬜
Implements [DD-11](#dd-11--profiles--content-service-access) (the profile ladder) and
[DD-12](#dd-12--unified-authorization-solverauth--authorizationsjson) (the unified RBAC
kernel) — a **prerequisite for Phase 5**, whose content routes need the kernel to exist.
It replaces the shell-only `commands.csv` + the web-only profile-on-user-record with one
policy (`authorizations.json`) enforced on both surfaces. Built shell-first (fully testable
with no web), then wired into the live auth service, then migrated. The **OS second layer**
(per-profile service instances + content-tree ACLs, DD-12) is *not* here — it is built with
the services it instantiates (content in Phase 5, ws in Phase 6); 4a delivers the policy
kernel, enforcement, and migration.

**Build order** (each step independently landable/testable):

1. **`solver/auth` kernel (shell-side).** New sub-package: `Subject(user, channel,
   auth_method, profile, permissions)`; the `authorizations.json` loader
   (`profiles`/`users`/`objects` + single-parent inheritance expansion); `resolve_subject()`
   (absorbs `solver/utils/identity.py` — ticket / owner-uid floor / os-login map, per DD-12);
   the registration-time `requires ⊆ perms` check and a **runtime `subject.has(obj:perm)`**
   query. Reads `/etc/euler/authorizations.json`, falling back to a repo default for dev.
   **Test:** unit tests for inheritance expansion, the three resolution planes, and
   fail-closed — no web needed.
2. **Decorator `requires=` / `channels=`; retire `commands.csv`.** Add both params to
   `@register`/`@command`; enforce `channel ∈ channels` **and** `requires ⊆ perms` at
   registration; **no-`requires` ⇒ fail-closed `infra:execute`**. Delete `commands.csv`,
   `_authorization_policy()`, `is_authorized*`; slim `modules.csv` to `(module,
   registers_commands)` and update `shell/loader.py`. **Test:** the local owner (admin) sees
   every command; a dev profile override hides the right ones.
3. **Annotate every command.** Add `requires=`/`channels=` to all commands per the DD-12
   mapping (`show → solutions:read`, `edit`/`new → solutions:write`, `evaluate`/`benchmark →
   solutions:execute`, `!` → `shell:execute`, `claude-* → ai:execute`, `git-*`/`key-* →
   infra:execute`, `users list → users:read` / mutations → `users:write`, `update-docs →
   channels=('terminal',)`, …). Regenerate the audit view **`solver/commands.json`** and
   `commands-index.md` via `update-docs`. **Test:** `commands.json` matches intent; the
   per-profile command set is correct; `flake8`/`mypy` clean.
4. **`authorizations.json` SoR + install seeding.** A kit (`scripts/setup/authz.sh`, or
   folded into `auth.sh`) deploys `/etc/euler/authorizations.json` (`root:root 0644`) from
   the repo bootstrap template, **seeds the checkout owner as `admin`**, and migrates the
   live accounts (`vikas.munshi@…` → `maintainer`, `vikasmunshi@…` → `contributor`,
   `mercanther@…` → `reader`). **Test:** the file exists with the right ownership/mode; the
   local shell resolves `admin`.
5. **Auth-service integration.** `euler-auth` resolves the profile from
   `/etc/euler/authorizations.json` (drop the `profile` field from `users.json` / the SRP
   record); `forward_auth` returns `X-Profile` from the map; the shell ticket carries the
   map profile. Redeploy via `auth.sh upgrade`. **Test:** `forward_auth`'s `X-Profile`
   matches the map; a later `users change` takes effect on re-login.
6. **`users` command rework.** Two-path `add` (`@`-address → web invite; bare os-login →
   direct map entry); add `users change`; split `users list` (`users:read`, non-sudo roster
   from the world-readable SoR) from the mutating verbs (`users:write`, sudo, editing the
   root-owned SoR + the SRP record for web accounts). **Test:** `users list` as a non-admin
   shows the roster; `users add <os-login> <profile>` adds a map entry; `users change`
   promotes + revokes sessions; mutations prompt for `sudo`.
7. **Cleanup + regression.** Remove `commands.csv` and every reference; `update-docs
   --check` clean; the full test suite + the Phase-4 auth/flow harnesses green (no
   regression). **Test:** end-to-end — register/login still work; a `reader` web session's
   `forward_auth` yields `X-Profile: reader`; the local owner is `admin`.

- **Deliver:** `solver/auth` (the shared RBAC kernel + identity), the `requires`/`channels`
  decorator, `authorizations.json` as the SoR under `/etc/euler`, the reworked `users`
  command, and the live-account migration — `commands.csv` retired, profile off the SRP
  record.
- **Kit:** `authz.sh` (deploy/seed/migrate the SoR) or folded into `auth.sh`; `update-docs`
  emits `commands.json`; no new runtime dependency.

### Phase 5 — Content service ⬜
**Prerequisite: Phase 4a** (the `solver/auth` kernel + `authorizations.json`) — the content
routes below are gated by its `requires`/`X-Profile` check, and their per-profile service
instances + content-tree ACLs (the DD-12 OS layer) are built here. Four independently
shippable sub-steps:

- **5a — Home, navigation, look & feel.** `base.html` + partials, shared CSS, header/nav,
  **htmx** vendored and wired for fragment-swap navigation. A **placeholder panel stands
  in for the web shell** so the layout and liveness are demonstrable before Phase 6.
  Establishes the full-page-vs-block rendering contract.
- **5b — View paths.** Server-rendered summary, problem, code, and docs pages, reading
  each problem's `solution_dir` (plaintext, incl. decrypted `solutions/private`).
- **5c — Content validation.** Port the `.py`/`.c`/`.json` reject-and-restore checks;
  **add the `.html` gate via [nh3](#47--content-security-policy--nh3)**, sanitize-and-store-clean
  ([DD-10](#dd-10--phase-5-content-service-choices)).
- **5d — Edit paths.** htmx save/delete/eval/benchmark returning rendered fragments (via
  the DD-10 block-render helper); benchmark progress via SSE. Every write goes through 5c;
  every response carries CSP.

**Design decisions:** the four content-service choices (nh3 gate, fragment mechanism,
notes format, html5lib) are **resolved** — see
[DD-10](#dd-10--phase-5-content-service-choices).

### Phase 6 — Web shell ⬜
The PTY-backed interactive `solver` shell over WebSocket, **reusing**
`web/pty_bridge.py` + `web/pty_manager.py` (one persistent shell per user). Replaces the
5a placeholder with the live terminal (`xterm.js`). Highest-risk service (RCE by design):
its own unit/user (`euler-ws`), egress only via Squid, behind `forward_auth`, and it
mints/redeems the DD-9 shell ticket at attach. Per-user helper uids/namespaces are a
future hardening (see [security-notes AR-1](security-notes.md)).

## 7 · Verify

1. `scripts/setup/frontend.sh status` shows Caddy + acme.sh installed, cert expiry,
   `euler-caddy.service` `active/enabled`, and `/healthz → HTTP 200`.
2. `sudo caddy validate --config /etc/euler/Caddyfile` passes; the service logs the
   loaded certificate with no ACME attempt.
3. From a LAN device, `curl -v https://<FQDN>/healthz` returns `ok` over a valid,
   browser-trusted certificate; `curl -sI https://<FQDN>/login` shows HSTS + CSP.
4. `scripts/setup/firewall.sh status` — an allowed uid (`euler-ddns` → ipify) reaches the
   net, a dropped uid (`euler-caddy`) does not; `smtp.sh test` delivers a probe mail.
5. Auth end-to-end and masquerade checks: see [access-control § 8](access-control.md).
6. For public access, add the router forward + firewall rule, wire DDNS, and re-test from
   outside the LAN (only once auth is in place).

## 8 · Sources

- [acme.sh](https://github.com/acmesh-official/acme.sh) ·
  [dnsapi guide](https://github.com/acmesh-official/acme.sh/wiki/dnsapi) ·
  [running under sudo](https://github.com/acmesh-official/acme.sh/wiki/sudo)
- [Caddy `tls` directive (manual certificates)](https://caddyserver.com/docs/caddyfile/directives/tls) ·
  [`forward_auth`](https://caddyserver.com/docs/caddyfile/directives/forward_auth)
- [Accessing network applications with WSL — Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/networking) ·
  [Hyper-V Firewall — Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/hyper-v-firewall)
- [nftables wiki](https://wiki.nftables.org/) · [Squid](http://www.squid-cache.org/) ·
  [htmx](https://htmx.org/) · [nh3](https://nh3.readthedocs.io/)
