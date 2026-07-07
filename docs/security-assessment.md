# Security Assessment — solver-web

**Target:** `solver-web` aiohttp front end, self-hosted at `https://euler.vikasmunshi.com`
(home network, Caddy TLS → `127.0.0.1:8080`).
**Date:** 2026-07-06
**Method:** source review of `solver/web/**`, `solver/shell/**`, `solver/crypto/**`,
`solver/utils/identity.py`, `Caddyfile`, and on-disk secret/permission checks. The
critical path-traversal finding was confirmed against the live aiohttp router; no
authenticated requests were issued against the running server.

This document is the remediation tracker. Fix findings one at a time; after each fix,
run the **Validation** step for that finding and tick its status box. A finding is
**Verified** only when its validation passes *and* the originally-confirmed exploit no
longer works.

---

## How to read this

Each finding has a stable ID (`SEC-NN`) that will not change even as items are closed,
so commits and tests can reference it. Severities follow impact-given-access, and note
the access required (all findings except the design note assume an authenticated
account, which is invite-only).

Status legend: `[ ] Open` · `[~] Fixed (pending validation)` · `[x] Verified`.

---

## Summary

| ID | Severity | Status | Finding |
|------|----------|--------|---------|
| [SEC-01](#sec-01--authenticated-arbitrary-file-read-absolute-path-traversal) | **Critical** | [x] Verified | Authenticated arbitrary file read via absolute-path traversal in the file viewer/editor |
| [SEC-02](#sec-02--authenticated-login-is-host-code-execution-design) | **High** | [ ] Open | Authenticated login is host code execution (edit+evaluate / claude-skill); needs OS sandboxing |
| [SEC-03](#sec-03--stored-xss-via-editable-html-solution-files) | **Medium** | [ ] Open | Stored XSS via editable `.html` solution files served as `text/html` |
| [SEC-04](#sec-04--x-forwarded-for-spoofing--rate-limiter-bypass) | **Medium** | [x] Verified | `X-Forwarded-For` is client-spoofable → rate-limiter bypass + log poisoning |
| [SEC-05](#sec-05--missing-edge-security-headers-hsts-csp) | **Medium** | [~] Fixed (browser-verify math) | Missing HSTS and Content-Security-Policy |
| [SEC-06](#sec-06--ai-commands-spend-owner-budget--run-agents-as-user) | **Medium** | [ ] Open | `claude-api` / `claude-skill` available to `user`: spends owner API budget, runs host agent |
| [SEC-07](#sec-07--env-world-readable) | **Low** | [x] Verified | `.env` is world-readable (0644) and holds the API key |
| [SEC-08](#sec-08--no-origin-check-on-the-websocket-endpoint) | **Low** | [ ] Open | No `Origin` check on `GET /ws` (CSWSH defence-in-depth) |
| [SEC-09](#sec-09--web-auth-grants-plaintext-read-of-all-private-solutions-design) | **Low/Info** | [ ] Open | Web auth = plaintext read of all `solutions/private/` (design note) |

See [What's done well](#whats-done-well) for the controls that are already sound and
must not regress, and [Red-team narrative](#red-team-narrative) for the end-to-end
attack chain that motivates the priority order.

---

## SEC-01 — Authenticated arbitrary file read (absolute-path traversal)

- **Severity:** Critical
- **Status:** [x] Verified — fixed 2026-07-06 (see [Resolution](#sec-01-resolution)).
- **Access required:** any authenticated account, including the lowest-privilege `guest`.
- **Location:** `solver/web/app.py` — `_resolve_solution_file` (serving `GET /{n}/{file}`)
  and `_edit_file` (serving `GET /edit/{n}/{file}`).

### Description

The traversal guard rejects only `..`:

```python
if '..' in Path(filename).parts:      # _resolve_solution_file
    raise web.HTTPNotFound()
```

It does not reject an **absolute** `filename`. Because
`problem.solution_dir.joinpath('/etc/passwd')` discards the base directory and returns
`/etc/passwd`, an absolute path escapes the solution tree. The route pattern
`/{problem_number:\d+}/{filename:.+}` binds an absolute value, and the aiohttp router
delivers it decoded.

The **write** path (`_save_content`, `_del_solution`) is *not* affected — it enforces
`Path(filename).name == filename`, rejecting any separator. Only the two **read** paths
are vulnerable.

### Reproduction (confirmed)

Router resolution was verified: for both request paths below, aiohttp binds
`filename='/etc/passwd'`.

```
GET /1//etc/passwd
GET /1/%2Fetc%2Fpasswd            # encoded form; survives proxy //-collapsing
```

The `%2F` form matters because Caddy forwards the encoded path to the upstream, so even
if `//` were normalised at the proxy, the encoded variant still reaches aiohttp and
decodes to an absolute path. Requires a valid session cookie (all routes are gated).

Contrast: `GET /1/../../../etc/passwd` **is** correctly blocked by the `..` check.

### Impact

The server runs as OS user `vikas`, so this reads any file that user can read:

- `keys/.user-pass` + `keys/.id` + `keys/enc-key.json` → reconstruct the AES master key
  offline → decrypt the **entire** `solutions/private/` history from the ciphertext that
  is public on GitHub. Total defeat of encryption-at-rest.
- `.env` → `ANTHROPIC_API_KEY` disclosure.
- `keys/.users.json` → SRP verifiers (offline cracking; the 16-char policy slows but does
  not eliminate this).
- `~/.ssh/id_*` and any other host secret → lateral movement / pivot.

Note: this does **not** yield live web sessions (in-memory only) nor forge remember-me
tokens (stored as `HMAC(validator)`, preimage-resistant) — so in-app privilege
escalation is limited — but the crypto and host-secret disclosure alone make it critical.

### Remediation

Contain the resolved path to the solution directory, mirroring the already-correct
`_serve_vendor_asset` pattern in the same file:

```python
base = problem.solution_dir.resolve()
target = problem.solution_dir.joinpath(filename).resolve()
if base != target and base not in target.parents:
    raise web.HTTPNotFound()
```

Apply to **both** `_resolve_solution_file` and `_edit_file`. After deploying, rotate the
crypto master key, `ANTHROPIC_API_KEY`, and `keys/.session-secret`, since prior
exposure cannot be ruled out.

### Validation

1. With a valid session, `GET /1/%2Fetc%2Fpasswd` and `GET /1//etc/passwd` both return
   **404** (not file contents).
2. `GET /edit/1/%2Fhome%2Fvikas%2Feuler%2Fkeys%2F.users.json` returns **404**.
3. Legitimate access still works: `GET /1/` and a real solution file (e.g.
   `GET /7/p0007_s0.py`) still resolve, and subdir resources (`resources/…`) still load.
4. Regression test asserting a 404 for an absolute/`%2F`-encoded `filename` on both the
   viewer and editor routes.

### <a id="sec-01-resolution"></a>Resolution (2026-07-06)

**Fix.** `_resolve_solution_file` (`solver/web/app.py`) — the single guard shared by the
viewer (`_problem_file`) and editor (`_edit_file`) routes — now resolves the target and
confirms it stays under the problem's solution directory, in addition to the existing
`..` check:

```python
base = problem.solution_dir.resolve()
target = problem.solution_dir.joinpath(filename).resolve()
if base != target and base not in target.parents:
    raise web.HTTPNotFound()
```

This mirrors the already-correct containment in `_serve_vendor_asset`. Because both read
routes funnel through this function, one change closes both. The write/delete paths were
never affected (they enforce `Path(filename).name == filename`).

**Regression test.** `tests/test_web_path_traversal.py` — drives `_resolve_solution_file`
directly and asserts:
- absolute filenames (`/etc/passwd`, `keys/.users.json`, `.env`) → `HTTPNotFound`;
- `../…` still → `HTTPNotFound`;
- legitimate solution files, `resources/…` subdir files, and the synthesised `solutions`
  listing still resolve;
- the aiohttp router genuinely binds `filename='/etc/passwd'` for `/7//etc/passwd` **and**
  `/7/%2Fetc%2Fpasswd` — proving the tested guard sits on the real attack path.

**Validation results.**
- `python -m unittest tests.test_web_path_traversal` → 6 passed.
- `python -m unittest discover -s tests` → 105 passed (no regressions).
- `flake8 solver/web/app.py tests/test_web_path_traversal.py` → clean.
- `mypy solver/web/app.py` → clean.
- The originally-confirmed exploit (`/7/%2Fetc%2Fpasswd`) now resolves to `HTTPNotFound`
  instead of returning file contents.

**Post-fix action still recommended:** rotate the crypto master key, `ANTHROPIC_API_KEY`,
and `keys/.session-secret`, since exposure prior to the fix cannot be ruled out.

---

## SEC-02 — Authenticated login is host code execution (design)

- **Severity:** High
- **Status:** [ ] Open
- **Access required:** any `user`-profile account (or `admin`).
- **Location:** `solver/commands.csv`, `solver/core/evaluate.py`, `solver/ai/skill.py`,
  the PTY shell (`solver/web/pty_bridge.py`).

### Description

Gating `!`/`bash` to `admin` in `commands.csv` does **not** contain the shell. The `user`
profile is granted `new` + `edit` + `evaluate`/`benchmark`: write arbitrary Python into a
solution file, then run it — `evaluate` executes it as `vikas`. `claude-skill` (also
`user`) launches a headless Claude Code agent with tool access on the host, an even more
direct execution vector.

The effective trust boundary is therefore **"who receives an invite,"** not the command
policy. This is a defensible design for trusted collaborators, but it means the service
is remote code execution as `vikas` for every non-guest account, hosted from a home
network — so a single leaked/rogue `user` credential is host compromise, and SEC-01
compounds it.

### Impact

Full code execution as `vikas` (reverse shell, secret theft, pivot). Amplifies every
other finding: with SEC-02 access, an attacker need not bother with SEC-01's cleverness.

### Remediation (pragmatic, layered — do the OS sandbox first)

1. Run the detached server **and** its forked PTY shells under a dedicated unprivileged
   user, inside a container/VM or a systemd sandbox: `NoNewPrivileges=`, `ProtectHome=`,
   `PrivateTmp=`, `ReadWritePaths=` scoped to the repo only, a seccomp profile, and
   resource limits. This also blunts SEC-01's blast radius.
2. Move the crypto master-key material (`keys/.id`, `keys/.user-pass`), `~/.ssh`, and
   `.env` out of any path that process can read; supply the API key via an environment
   file the sandbox controls, not a repo-relative `.env`.
3. Treat every invited account as equivalent to handing out a shell; keep the invite list
   minimal and audited.

### Validation

1. `ps`/`systemctl show` confirms the server and a forked PTY child run as the dedicated
   non-`vikas` user.
2. From an authenticated shell, `evaluate` of a solution that attempts to read
   `keys/.user-pass` or `~/.ssh/id_*` fails (permission denied / not visible).
3. `systemd-analyze security caddy-euler.service` (and the solver-web unit) shows the
   hardening directives applied.

---

## SEC-03 — Stored XSS via editable `.html` solution files

- **Severity:** Medium
- **Status:** [ ] Open
- **Access required:** any `user` (write); any authenticated viewer is the victim.
- **Location:** `solver/web/app.py` — `_save_content` (writes `.html` unvalidated) and
  `_problem_file` (serves `.html` as `text/html`).

### Description

`_save_content` accepts `.html` and writes it verbatim (no sanitisation). `_problem_file`
serves an `.html` solution file back with `Content-Type: text/html` as raw bytes. A
`user` can therefore store JavaScript in a `notes.html` that executes same-origin in
another user's (e.g. an admin's) browser on `GET /{n}/notes.html`. No CSP is present to
contain it.

### Impact

Stored XSS between authenticated users: session-scoped actions in the victim's browser
(e.g. driving an admin to admin-only endpoints), same-origin data exfiltration. Bounded
to authenticated users and `SAMEORIGIN` framing, but real.

### Remediation

- Serve solution `.html` with `Content-Type: text/plain` (render it in the code viewer,
  not as live HTML), **or** sandbox it (isolated origin / `sandbox` iframe).
- Add a restrictive Content-Security-Policy (see SEC-05) as defence-in-depth.

### Validation

1. Save a `notes.html` containing `<script>document.title='xss'</script>`; `GET
   /{n}/notes.html` returns it as inert text (or sandboxed), and the script does not run.
2. Response `Content-Type` for `.html` solution files is not `text/html` (or CSP blocks
   inline script execution).

---

## SEC-04 — `X-Forwarded-For` spoofing → rate-limiter bypass

- **Severity:** Medium
- **Status:** [x] Verified — fixed 2026-07-06 (see [Resolution](#sec-04-resolution)).
- **Location:** `solver/web/auth/routes.py` — `_client_ip`; `Caddyfile`.

### Description

`_client_ip` trusts the **first** `X-Forwarded-For` hop:

```python
forwarded = request.headers.get('X-Forwarded-For')
if forwarded:
    return forwarded.split(',')[0].strip()
```

Caddy's `reverse_proxy` **appends** the real peer to any client-supplied XFF, so a
request carrying its own `X-Forwarded-For:` header lands that value first. The auth
rate-limiter (`RATE_LIMITED` endpoints) keys on this, so rotating a spoofed header defeats
the throttle; any XFF-derived logging is likewise poisoned.

### Impact

Brute-force throttle bypass on the unauthenticated auth/register endpoints (SRP + 16-char
policy still make cracking hard, so this is defence-in-depth loss, not direct breach) and
untrustworthy client-IP logs.

### Remediation

- Caddyfile: overwrite rather than append, so the client cannot inject —
  `reverse_proxy 127.0.0.1:8080 { header_up X-Forwarded-For {remote_host} }`; **or**
- App: with exactly one trusted proxy on loopback, take the **rightmost** XFF hop (or use
  aiohttp's trusted-proxy handling) instead of `split(',')[0]`.

### Validation

1. A request with a forged `X-Forwarded-For: 1.2.3.4` to `/auth/challenge` is rate-limited
   against the real peer IP, not `1.2.3.4` — sending >30 such requests in a minute from
   one host trips the limiter regardless of the header value.
2. Server-side client-IP logging shows the real peer, not the spoofed value.

### <a id="sec-04-resolution"></a>Resolution (2026-07-06)

**Fix — two layers.**
- App (`solver/web/auth/routes.py`, `_client_ip`): trust the **rightmost** `X-Forwarded-For`
  hop instead of the left-most. With one trusted proxy that appends the real peer last, the
  rightmost value is the one a client cannot forge; the old `split(',')[0]` trusted the
  spoofable left-most value, letting a caller mint a fresh rate-limit bucket per request.
- Edge (`Caddyfile`): `reverse_proxy … { header_up X-Forwarded-For {remote_host} }` overwrites
  the header with the real transport peer, so a client-supplied value never reaches the app.
  Belt-and-suspenders: the app is correct whether Caddy overwrites or appends. The Caddyfile
  is generated (and gitignored), so this lives in the tracked generator
  `scripts/setup/caddy.sh` (`generate_caddyfile`); regenerate with `caddy.sh install`/`service`
  and `caddy reload` to deploy.

**Regression test.** `tests/test_auth_routes.py::test_rate_limit_keys_on_rightmost_xff_hop`
— sends `X-Forwarded-For: 10.0.0.<i>, 9.9.9.9` (a rotating spoofed prefix + a fixed
appended peer) and asserts the limiter keys on `9.9.9.9`, returning 429 after the window
is exhausted despite the changing prefix. The old left-most logic would never have tripped.

**Validation results.**
- `python -m unittest tests.test_auth_routes` → passes (incl. the new test and the existing
  `test_rate_limit_returns_429`).
- `caddy validate --config Caddyfile` → *Valid configuration*.
- Full suite (106) green; flake8 + mypy clean.

---

## SEC-05 — Missing edge security headers (HSTS, CSP)

- **Severity:** Medium
- **Status:** [~] Fixed 2026-07-06 — one browser check outstanding (see [Resolution](#sec-05-resolution)).
- **Location:** `Caddyfile`; `solver/web/auth/routes.py` — `_add_security_headers`.

### Description

Responses set `X-Content-Type-Options`, `X-Frame-Options`, and `Referrer-Policy` but no
`Strict-Transport-Security` and no `Content-Security-Policy`. TLS is terminated at Caddy,
so HSTS belongs there; CSP is feasible because the front end inlines its own assets and
already blocks external hosts.

### Impact

No HSTS → SSL-strip / downgrade window on first contact. No CSP → nothing contains an
injected script (compounds SEC-03).

### Remediation

- Caddyfile: add `header Strict-Transport-Security "max-age=31536000; includeSubDomains"`.
- Add a restrictive CSP (`default-src 'self'`, tightened for the terminal/editor pages;
  audit inline script/style needs and prefer nonces/hashes over `'unsafe-inline'`).

### Validation

1. `curl -sI https://euler.vikasmunshi.com/login` shows `Strict-Transport-Security` and
   `Content-Security-Policy`.
2. With CSP deployed, the SEC-03 probe script does not execute (CSP violation in console).
3. The terminal, viewer, and editor pages still function (no CSP breakage).

### <a id="sec-05-resolution"></a>Resolution (2026-07-06)

**Fix.**
- HSTS (`Caddyfile`): `header Strict-Transport-Security "max-age=31536000; includeSubDomains"`.
  Safe because the site is HTTPS-only (DNS-01, no `:80`). `preload` intentionally omitted.
  Baked into the tracked generator `scripts/setup/caddy.sh` (`generate_caddyfile`), since the
  Caddyfile itself is generated and gitignored.
- CSP (`solver/web/auth/routes.py`, `_add_security_headers`), applied to every response:

  ```
  default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
  img-src 'self' data:; font-src 'self' data:; connect-src 'self';
  frame-ancestors 'self'; base-uri 'self'; form-action 'self'; object-src 'none'
  ```

  `script-src 'self'` carries **no** `'unsafe-inline'` and **no** `'unsafe-eval'`, so an
  injected inline `<script>`/event handler (the SEC-03 stored-XSS vector via editable
  `notes.html`) is blocked. This is safe because the front end is fully self-contained
  (xterm/codemirror/mathjax/highlight.js are all vendored under `/vendor`), and MathJax's
  only `eval`/`Function` sites are a Node-only branch (`typeof process`) and a `globalThis`
  fallback wrapped in `try/catch` — both unreachable in a modern browser. `'unsafe-inline'`
  is kept for `style-src` alone (codemirror/mathjax/xterm inject inline styles; style
  injection cannot run script). WebSocket `/ws` is same-origin (`connect-src 'self'`).

- To satisfy strict `script-src`, the single inline `<script>` in `web-content/docs/docs.html`
  (used by the `/docs/*` and `/ai/*` pages) was moved to `web-content/docs/docs.js`
  (allow-listed in `_STATIC_ASSETS`).

**Regression test.** `tests/test_auth_routes.py::test_security_headers_present` — asserts
CSP is present, contains `default-src 'self'` / `script-src 'self'` / `object-src 'none'`,
has no `unsafe-eval`, and no `unsafe-inline` inside the `script-src` directive.

**Validation results.**
- Full suite (106) green; flake8 + mypy clean; `caddy validate` → *Valid configuration*.
- `/docs.js` confirmed to resolve via the static handler; no inline `<script>` remains in
  `docs.html`.

**Outstanding (why status is Fixed, not Verified):** the CSP has not yet been exercised in a
real browser. Before ticking to Verified, load a **problem page** (MathJax/LaTeX renders),
the **terminal**, and the **code editor**, and confirm no CSP violations in the devtools
console. If MathJax misbehaves on an old browser, the minimal fallback is adding
`'unsafe-eval'` to `script-src` (still blocks the SEC-03 injection vector). Also run
validation step 1 (`curl -sI`) against the live site after deploying the Caddyfile.

---

## SEC-06 — AI commands spend owner budget / run agents as `user`

- **Severity:** Medium
- **Status:** [ ] Open
- **Location:** `solver/commands.csv` (`claude-api`, `claude-skill` granted to `user`);
  `solver/ai/api.py`, `solver/ai/skill.py`.

### Description

Both AI entry points are available to the `user` profile. `claude-api` spends the owner's
`ANTHROPIC_API_KEY` on every call; `claude-skill` launches an autonomous Claude Code agent
that edits files and runs on the host (an execution amplifier for SEC-02).

### Impact

Uncapped billing abuse by any invited user, and an additional host-execution path.

### Remediation

Make `claude-api`/`claude-skill` `admin`-only in `commands.csv`, **or** add per-user
quotas/budget caps and audit logging. Regenerate the command docs (`update-docs`) after
changing the policy.

### Validation

1. A `user`-profile shell reports `claude-api`/`claude-skill` as unknown/not-permitted
   (unregistered), and the `/authz?cmd=claude-api` check returns `false` for `user`.
2. If quotas are chosen instead: exceeding the cap is refused with a clear error, and
   spend is logged per user.

---

## SEC-07 — `.env` world-readable

- **Severity:** Low
- **Status:** [x] Verified — fixed 2026-07-07 (see [Resolution](#sec-07-resolution)).
- **Location:** `/home/vikas/euler/.env` (observed mode `0644`).

### Description

`.env` holds `ANTHROPIC_API_KEY` yet is world-readable. Low risk on a single-user host,
but any local account (or a process running as another user) can read the key.

### Remediation

`chmod 600 .env` (and confirm it stays gitignored — currently it is). Prefer supplying the
key via the sandbox's environment (SEC-02) over a repo-relative file.

### Validation

1. `stat -c '%a' .env` → `600`.
2. `git check-ignore .env` still reports it ignored.

### <a id="sec-07-resolution"></a>Resolution (2026-07-07)

**Fix.** The file was relocated to `keys/.env` — alongside the other secrets, all mode
`600` — and set to mode `600` itself. Its location is now a single config item,
`config.env_file` (`solver/config.py`), consumed by `get_api_key`
(`solver/ai/models.py`), the SMTP mailer (`solver/web/auth/mail.py`), identity
resolution (`solver/utils/identity.py`, via a `resolve_identity` parameter), and
`scripts/setup/acme.sh`.

**Validation results** (against the new path):
- `stat -c '%a' keys/.env` → `600`.
- `git check-ignore keys/.env` → still ignored (the `**/.*` rule).
- `config.env_file` resolves to `keys/.env`; `get_api_key()` and the SMTP credential
  lookup both read it there (verified live); full suite (106) green.

The remediation's second preference — supplying the key via a sandbox-controlled
environment rather than any repo-relative file — remains part of SEC-02.

---

## SEC-08 — No `Origin` check on the WebSocket endpoint

- **Severity:** Low
- **Status:** [ ] Open
- **Location:** `solver/web/app.py` — `_ws_handler` (`GET /ws`).

### Description

`_ws_handler` does not validate the `Origin` header. Cross-Site WebSocket Hijacking is
**mitigated today** by `SameSite=Strict` session cookies (a cross-site WS handshake
won't carry the cookie), but relying on a single control is fragile.

### Impact

Defence-in-depth gap: if the cookie policy ever regressed, a malicious page could attach
to a victim's terminal.

### Remediation

Reject the `/ws` upgrade when `Origin` is present and not the site's own origin.

### Validation

1. A WS handshake to `/ws` with `Origin: https://evil.example` is rejected (4xx / close),
   while same-origin `Origin: https://euler.vikasmunshi.com` succeeds.

---

## SEC-09 — Web auth grants plaintext read of all private solutions (design)

- **Severity:** Low / Informational
- **Status:** [ ] Open
- **Location:** whole viewer/editor surface; `solutions/private/**`.

### Description

Every authenticated user has read (and, for `user`, write) access to the **decrypted**
`solutions/private/` tree via the viewer/editor. This is inherent to a shared solver, but
it relaxes the project's "plaintext never leaves the repo" rule to "plaintext is served to
any authenticated web user." There is also no per-user isolation on the solution tree —
any `user` can modify any solution, and (via `evaluate`) run the result.

### Impact

Confidentiality of private solutions extends to the full invited-user set, not just the
local operator. Accept-and-document, or restrict, per your intent.

### Remediation (choose per intent)

- Accept and document explicitly (update the confidentiality rule in `CLAUDE.md` / the
  auth docs to state that authenticated web users can read private plaintext), **or**
- Gate `solutions/private/**` behind a higher profile (e.g. `admin`-only viewer), **or**
- Add per-user ownership/ACLs on solutions if collaboration should be compartmentalised.

### Validation

1. The chosen policy is documented, or enforced (e.g. a `guest`/`user` request for a
   private-problem file returns 403 if you gate it).

---

## What's done well

These controls are sound; treat them as regression guards, not open items.

- **SRP-6a** (`solver/web/auth/srp.py`): the password never reaches the server or disk;
  correct `PAD`, `u≠0`/`A,B mod N≠0` checks, `secrets.compare_digest` throughout.
- **Anti-enumeration**: stable decoy salt/verifier for unknown emails (`decoy_token`).
- **Invite-only registration**: single-use, hashed, 24 h expiring secure-link tokens
  (`pending.py`); the account written is the token's bound email, never client-supplied.
- **Remember-me**: selector\:validator with rotation-on-use, theft detection (wrong
  validator revokes the selector), and `HMAC(validator)` at rest (preimage-resistant).
- **Secret hygiene**: atomic writes at mode `0600` (`users.py`, `remember.py`,
  `pending.py`); all secret dotfiles and `.env` are gitignored.
- **Network posture**: server binds `127.0.0.1` only; Caddy terminates TLS with an
  out-of-band DNS-01 cert.
- **Per-user isolation**: each web user gets a forked shell process resolved to their own
  profile; command registration is gated at import by `commands.csv`.
- **Write-path traversal is correctly blocked** (`_save_content` / `_del_solution`
  enforce `Path(name).name == name`).
- **Cookies**: `Secure`, `HttpOnly`, `SameSite=Strict`, site-wide.

---

## Red-team narrative

An attacker needs one thing: an invited account at any privilege level (phished/leaked
credential, or a rogue collaborator). From a bare `guest`:

1. `GET /1/%2Fhome%2Fvikas%2Feuler%2Fkeys%2F.user-pass`, `…/.id`, `…/enc-key.json`
   (SEC-01) → reconstruct the master key offline → `git clone` the public repo → decrypt
   every private solution ever committed.
2. `GET /1/%2Fhome%2Fvikas%2Feuler%2F.env` → exfiltrate the API key.
3. `GET /1/%2Fhome%2Fvikas%2F.ssh%2Fid_ed25519` → pivot off the box.

If the account is `user` rather than `guest`, they skip the cleverness (SEC-02): `edit` a
solution to spawn a reverse shell and `evaluate` it as `vikas`.

This chain is why the priority order is **SEC-01 first** (removes the guest-tier file
read and the crypto/secret disclosure), then **SEC-02** (OS sandbox, which also caps the
blast radius of anything missed), then the medium/low hardening items.
