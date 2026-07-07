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
| TLS / edge / routing | **Caddy** (reverse proxy, `forward_auth` gate), certs via **acme.sh** DNS-01 — reuse `scripts/setup/caddy.sh` + `scripts/setup/acme.sh`. |
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
            loopback / unix sockets                           ▼
        ┌───────────┬─────────────┬──────────────┐     ┌────────────┐
        ▼           ▼             ▼               ▼     │   auth      │  SRP login,
   ┌─────────┐ ┌──────────┐ ┌───────────┐              │  service    │  sessions,
   │ welcome │ │ content   │ │  ws /      │◀────────────│ (aiohttp)   │  forward_auth
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

Every app process binds loopback (or a unix socket); **only Caddy is publicly
bound**. Caddy authenticates every request through the auth service's
`forward_auth` endpoint before it reaches content or shell, so those services never
see an unauthenticated caller even if they have a bug.

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
  for purely static responses (the welcome page, vendored assets).
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
   - *System deps* (caddy, squid): apt repo + package, reusing the caddy.sh shape.
3. **Configuration** — generator for any host-specific config (Caddyfile, Squid
   allowlist, service env), gitignored when it carries a hostname/secret, generated
   at install from a CLI arg / env var / prompt (as caddy.sh does for the hostname).
4. **Lifecycle** — `start` / `stop` / `status` / `restart`. Prefer a **systemd unit
   per service** (the relocatable `caddy-euler.service` pattern), falling back to
   the detached-process + `fcntl.flock` model in `solver/web/cli.py` where systemd
   is absent. Each service is independently restartable.
5. **Health probe** — a `status` that reports actually-serving (flock/HTTP ping),
   not just "process exists".

An **umbrella orchestrator** (`solver-web` reworked, or a `make web-*` target)
composes the per-service lifecycles so the whole stack starts/stops/reports as one,
while each service remains independently operable.

---

## Phases

Built strictly in order; each is independently runnable and shipped with its full
[maintenance kit](#the-maintenance-kit-per-feature-contract). The stack is useful
and demonstrable at the end of every phase.

### Phase 1 — Caddy + ACME (edge)
- **Deliver:** public `:443` edge terminating TLS, auto-renewing cert, reverse-proxy
  skeleton routing to (initially nothing but) a health endpoint. Security headers +
  fallback CSP for static responses.
- **Reuse:** `scripts/setup/caddy.sh`, `scripts/setup/acme.sh`, the generated
  gitignored Caddyfile. Restructure the Caddyfile as the new topology's router
  (path-based upstreams, `forward_auth` block stubbed).
- **Kit:** install/uninstall/update Caddy + acme.sh; Caddyfile generator; systemd
  unit (`caddy-euler.service`); `status` via cert + HTTP ping.

### Phase 2 — Squid (egress)
- **Deliver:** forward proxy with a **domain allowlist** (`api.anthropic.com`,
  `projecteuler.net`, GitHub); default-deny. Nothing routes out except via it.
- **Wire:** `HTTPS_PROXY`/`HTTP_PROXY` in the service env used by AI features, the
  problem scraper, and `gh`. This operationalises the "plaintext must never leave
  the repo" rule at the network layer.
- **Kit:** install/uninstall/update squid; allowlist config generator; systemd unit;
  `status` that asserts allow + deny behaviour with a probe.

### Phase 3 — Dummy welcome page
- **Deliver:** a single static page served through Caddy end-to-end — proves TLS,
  routing, headers, and CSP fallback on a real response. No app framework yet.
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
