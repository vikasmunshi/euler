# `solver-web` server redesign

A ground-up rebuild of the web front end as a set of **isolated services** behind a
single edge, delivering **server-rendered pages that feel live** (no
skeleton-page + client-fetch architecture). This is the design of record for that
rebuild; it is the transport/app-layer companion to [tls-guide.md](tls-guide.md),
[authentication.md](authentication.md), and [authorization.md](authorization.md).

> Status: design. Built feature-by-feature (see [Phases](#phases)); each phase
> ships its full [maintenance kit](#the-maintenance-kit-per-feature-contract)
> before the next begins.

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
| Service identity | Dedicated system users `euler-caddy` / `euler-auth` / `euler-content` / `euler-ws` (in the **`euler-web`** group), plus `euler-proxy` for egress — see [DD-2](#design-decisions). |
| Edge setup & lifecycle | One `scripts/setup/frontend.sh` (install/uninstall/upgrade) installs **root-owned systemd units** (start/stop needs `sudo`), superseding `caddy.sh` + `acme.sh` — see [DD-3](#design-decisions). |
| Egress control | **Squid** forward proxy, domain allowlist; shell/AI/scrapers reach the network only via `HTTPS_PROXY`. |
| Response headers | **Content-Security-Policy on every served page** (see [CSP](#content-security-policy)). |

## Open decisions (this document argues, you choose)

- **Framework/templating**: aiohttp-only vs Jinja2 vs FastAPI → [decision](#framework--templating).
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
  `solver/web-content/vendor/` exactly like `xterm.js`/`codemirror` today (pinned +
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
     **pinned** version into `solver/web-content/vendor/`, records the **SRI hash**,
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

### Phase 3 — Maintenance page (static)
- **Deliver:** a single static **"site under maintenance"** page served through Caddy
  end-to-end — proves TLS, routing, headers, and CSP fallback on a real response. No
  app framework yet. Reusable later as the holding page Caddy serves when an upstream
  is down or during a deploy.
- **Establishes:** the `web-content` static layout and the CSP baseline the app
  services will inherit.
- **Kit:** the page + its assets; no new runtime dep; wired into Caddy routing.

### Phase 4 — Auth service
- **Deliver:** aiohttp auth service exposing (a) SRP login/session/remember-me/reset
  (reuse `web/auth/*`: `srp.py`, `sessions.py`, `remember.py`, `ratelimit.py`,
  `mail.py`) and (b) a **`forward_auth` endpoint** returning `200 + X-User…` or
  `401`. Caddy gates all downstream routes through it.
- **Deliver:** the **CSP middleware** (nonce minting) lives here and is shared with
  content. Login/register/password pages are the first Jinja-rendered pages.
- **Kit:** Python deps (aiohttp-jinja2, Jinja2) install/update/check; service env +
  session/key config; systemd unit + `status`; Caddy `forward_auth` block activated.

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
