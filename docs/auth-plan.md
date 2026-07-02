# Authentication design & implementation plan (solver-web)

> **Status: plan / not yet implemented.** Auth is implemented in **aiohttp**
> (`solver/web/`), not Caddy — Caddy stays a pure TLS reverse proxy. Prereq: the
> HTTPS front end from [`tls-setup.md`](tls-setup.md) (auth cookies require TLS).
> Target branch: `feature/web-srp-auth`, **rebuilt on current `master`** (the WIP
> there predates the workspace-lock removal and mixed auth with the master key —
> both corrected here).

## What we are protecting & why auth is mandatory

`GET /ws` hands any browser a full interactive `solver` shell (arbitrary RCE as
this user); `POST /<n>/…` writes files and runs commands. TLS encrypts the channel
but authenticates nobody. This feature is the access gate that must exist before
the server is ever exposed publicly (router forward + firewall stay closed until
it ships).

## Requirements (from the brief)

- **SRP** for authentication; **email as the username**.
- **Registration via emailed OTP** (invite-only — see Confirmed decisions): an
  invited email receives an **OTP via Gmail** → verify OTP → user sets their own
  password (**minimum complexity**) → account active.
- **Remember me** on login.
- Verifier store at **`keys/users.json`**.
- **Do not mix encryption keys and user-auth keys** — SRP/auth material is wholly
  separate from the git-filter master key (`.id` / `enc-key.json`).

## Separation of concerns (the no-mixing rule, made structural)

| Subsystem | Purpose | Lives in | Key material |
|---|---|---|---|
| Solution encryption | git clean/smudge of `solutions/private/` | `solver/crypto/` | `keys/.id`, `keys/enc-key.json` |
| **Web authentication** | gate the web front end | **`solver/web/auth/`** (new) | `keys/users.json`, `keys/.session-secret` |

The SRP code from the WIP currently sits in `solver/crypto/srp.py`; **relocate it to
`solver/web/auth/srp.py`** so encryption and auth share no module, no import path,
and no key material. Web login gates *access only*; decrypting private solutions
still flows through the existing `.id`/`.user-pass` path, untouched and independent.

## SRP style: browser-side SRP-6a (decided)

SRP-6a's distinctive property is that the **password never crosses the wire** — the
browser proves knowledge via a challenge/response and the server stores only a
verifier. The WIP's `verify_password()` instead runs SRP *server-side* from a
POSTed password (password crosses the wire, TLS-encrypted).

**Decided: true browser-side SRP-6a** — the reason to choose SRP over a plain Argon2
password hash; otherwise SRP degrades to "a fancier hash at rest."

Consequence to accept: because the server never sees the password, **password-complexity
is enforced client-side** (in the browser, before the verifier is computed). For a
small, trusted user set that's fine — a user only weakens their own account. If you'd
rather enforce complexity server-side, that requires the server to see the password
(the WIP's server-side `verify_password` path over TLS) — the simpler fallback,
noted where relevant below.

The server side (`SrpServer`, verifier format) is ~90% done in the WIP; the new work
is a browser SRP client interoperable with the Python parameters (RFC 5054 2048-bit,
`g=2`, SHA-256, left-pad to `|N|`).

## Data model

### `keys/users.json` (gitignored via `**/.*`? no — see note)

> ⚠️ `users.json` is **not** a dotfile, so add an explicit `keys/users.json` line to
> `.gitignore` (verifiers + salts are sensitive; never commit).

```json
{
  "version": "srp6a-sha256-2048",
  "users": {
    "user@example.com": {
      "salt": "<hex>",
      "verifier": "<hex>",
      "created": "<iso8601>",
      "disabled": false
    }
  }
}
```

Keyed by normalized email (lowercased, trimmed). Stored as `{salt, verifier}` only —
no password, no password-equivalent. Serialized/loaded through a small `UserStore`
(atomic write, `0600`).

### `keys/.session-secret` (gitignored dotfile)

32 random bytes, generated + persisted `0600` on first run (mirrors how the WIP
auto-generated its login password). HMAC key for remember-me tokens. An app secret —
**not** in `solver/crypto`.

### In-memory (per-process) state

- **Pending registrations**: `email → {otp_hash, expires, attempts}` (short TTL;
  a restart simply cancels in-flight registrations).
- **Pending SRP logins**: `email → {b, B, expires}` ephemeral server values between
  the challenge and verify steps.
- **Sessions**: `token → {email, expires}` (restart logs everyone out — remember-me
  restores them, below).

## Modules (new, under `solver/web/auth/`)

- `srp.py` — relocated from `solver/crypto/srp.py` (SrpServer + verifier/token helpers).
- `users.py` — `UserStore` over `keys/users.json` (load/save/get/add/disable, atomic).
- `otp.py` — OTP generate/verify (numeric, hashed at rest in the pending map) + the
  Gmail SMTP sender.
- `sessions.py` — session table + remember-me token mint/verify (HMAC selector:validator).
- `routes.py` — the aiohttp handlers + the `@web.middleware` gate.
- `policy.py` — password/OTP policy constants (mirrored by the client for complexity).

## Registration (invite-only) + OTP flow

Registration is **invite-only**: there is no public "request an account" endpoint.
An admin authorizes an email from the shell with **`users add <email>`**, which seeds
a pending registration `{otp_hash, expires=+10 min, attempts=0}` and **emails the OTP
via Gmail**. The invited user then completes registration in the browser:

1. `POST /register/verify` `{email, otp}` → check TTL + attempts (lock after N tries);
   on match, mint a short-lived **registration ticket** (signed, ~10 min) authorizing
   a password set.
2. `POST /register/complete` `{email, ticket, salt, verifier}` → the browser has taken
   the chosen password (validated against the **client-side** complexity policy),
   generated a salt, and computed the SRP verifier; the server verifies the ticket and
   persists `{salt, verifier}` to `users.json`, marking the account active. Password/OTP
   never stored in clear.

The register page (`/register`, a public asset) collects email + OTP, then the new
password; the two endpoints above are on the public allow-list. There is **no** open
`POST /register` request endpoint — `users add` is the only way to start registration.

Gmail sending: `smtp.gmail.com:587` STARTTLS, login with the Gmail address + an
**App Password** (2-Step Verification is already on the account). Creds from `.env`:
`SMTP_ADDRESS`, `SMTP_APP_PASSWORD`. Send via `smtplib` in `run_in_executor` (matches
the app's existing blocking-call pattern).

## Login flow (SRP-6a, browser-side)

1. `POST /auth/challenge` `{email, A}` →
   - look up `{salt, v}`; compute `b`, `B = k·v + g^b`; stash ephemeral `{b,B}`;
     reply `{salt, B}`. (Return a decoy salt/`B` for unknown emails to avoid user
     enumeration.)
2. `POST /auth/verify` `{email, A, M1}` →
   - `SrpServer` computes `u, S, K`, checks `M1`; on success reply `{M2}` and open a
     **session** (cookie); on failure, generic 401.
3. Browser verifies `M2` (mutual auth), then it's logged in.

`remember=true` on step 2 additionally sets a persistent remember-me cookie (below).

## Sessions & remember-me

- **Session cookie** `solver_session`: opaque token → in-memory `{email, expires}`,
  short TTL (e.g. 12 h). Attributes: `Secure; HttpOnly; SameSite=Strict; Path=/`.
- **Remember-me cookie** `solver_remember` (only when requested): selector:validator
  pattern — server stores `selector → {email, HMAC(validator), expires}` in
  `keys/remember.json` (gitignored) so it **survives restarts**; the cookie holds
  `selector:validator`, long TTL (e.g. 30 d), same cookie attributes. On a request
  with no valid session but a valid remember cookie: verify (constant-time), **rotate**
  the validator (one-time-use), and open a fresh session. Logout clears both and
  deletes the server-side remember record.

## Middleware (the gate)

`@web.middleware` on `build_app`, allowing only:
`/login`, `/register`, `/register/verify`, `/register/complete`, `/auth/challenge`,
`/auth/verify`, `/logout`, and the login/register **static assets** (`login.*`,
`register.*`, the SRP client JS, favicon).

Everything else — pages, viewer, edit/cmd routes, and the **`/ws` PTY** — requires a
valid session (or a remember cookie promoted to one). For `/ws`, check the cookie in
`_ws_handler` **before** `ws.prepare()` and reject the upgrade (don't hand a socket to
an unauthenticated client). Browser navigations without a session redirect to
`/login?next=…` (sanitized to a same-site path); programmatic fetches get `401`.

The WIP's `_auth_middleware` / `_login_page` / session helpers in
`feature/web-srp-auth:solver/web/app.py` are a usable scaffold — port them, drop the
single shared-password model and any master-key/workspace-lock coupling.

## Frontend

Under `solver/web-content/`:

- `login/` — email + password form; on submit runs the **SRP client** (challenge →
  verify), then redirects to `next`.
- `register/` — three panes (request OTP → enter OTP → set password); the password
  pane enforces the **complexity policy** and computes `{salt, verifier}` locally.
- `auth/srp-client.js` — browser SRP-6a, **interoperable** with `srp.py`: same `H`
  (SHA-256), same `k=H(N|PAD(g))`, same `x=H(salt|H(email|":"|password))`, same
  `M1/M2` construction, and the same `PAD`-to-`|N|` on `A/B/S`. Use BigInt for modpow
  + WebCrypto for SHA-256. **Cross-test with shared vectors** generated by `srp.py`
  (a tiny `pytest` that pins `A,B,M1,M2,K` for a fixed `a,b,salt` and the JS reproduces
  them) — interop bugs here are silent auth failures.

(Vendoring a vetted lib like `tssrp6a` is an option, but its `M1`/hash conventions
differ from the custom `srp.py`; hand-matching + vectors is safer than reconciling.)

## Config & secrets

`solver/config.py` — add file paths (application config, **not** crypto):

```python
users_file: Path            # keys/users.json
remember_file: Path         # keys/remember.json
session_secret_file: Path   # keys/.session-secret
# __init__:
'users_file':          root_dir / 'keys' / 'users.json',
'remember_file':       root_dir / 'keys' / 'remember.json',
'session_secret_file': root_dir / 'keys' / '.session-secret',
```

`.env` — add `SMTP_ADDRESS`, `SMTP_APP_PASSWORD` (Gmail App Password). Policy/TTL
constants live in `auth/policy.py`. `.gitignore` — add `keys/users.json` and
`keys/remember.json` (dotfiles like `.session-secret` are already covered by `**/.*`).

## Shell commands (admin)

A small `users` command group (registered like other shell commands) for bootstrap
and management without the web flow:

- `users list` — emails + created/disabled state (never secrets).
- `users disable <email>` / `users enable <email>`.
- `users remove <email>`.
- `users add <email>` — **the** registration trigger (invite-only): create a
  **disabled, password-less** account, seed a pending OTP, and **email it** (falling
  back to printing the code on the console if SMTP is unconfigured). The invited user
  always chooses their own password in the browser — the shell never sets one and the
  server never sees it. `remove`/`disable`/`enable`/`list` manage existing accounts.

## Security considerations

- **Invite-only registration.** No public request endpoint; accounts are authorized
  one email at a time via `users add`, the only trigger for an OTP. This is the primary
  gate protecting the RCE shell.
- **User enumeration** — neutral responses on `/register` and decoy salt/`B` on
  `/auth/challenge`.
- **Brute force** — OTP attempt caps + TTL; login rate-limiting (Caddy edge
  rate-limit on `/auth/*` and `/register/*` as cheap defense-in-depth, plus per-email
  backoff in-app).
- **Timing** — constant-time compares for OTP, `M1`/`M2`, remember validators.
- **Cookies** — `Secure; HttpOnly; SameSite=Strict`; remember tokens single-use
  (rotate on each use), server-side revocable.
- **CSRF** — `SameSite=Strict` covers the main risk; state-changing POSTs are
  same-origin fetches from our pages.
- **No secrets in logs**; `users.json`/`remember.json`/`.session-secret` at `0600`.
- **Reset** — password reset reuses the OTP mechanism (later; same flow as register).

## Milestones (each a reviewable PR-sized step)

1. **Scaffold & separation** — create `solver/web/auth/`, relocate `srp.py` there,
   add `UserStore` + `users.json` schema + config paths + `.gitignore`. Unit tests
   for `srp.py` incl. the JS-interop vectors.
2. **Login (SRP) + sessions + middleware** — challenge/verify endpoints, session
   cookie, gate all routes incl. `/ws`; login page + `srp-client.js`. Bootstrap a
   user via `users add` + the OTP flow (M3). (Usable end-to-end: login
   required, no OTP invite yet.)
3. **Invite registration + OTP + Gmail** — `users add` (seed + send OTP), the
   `/register/verify` + `/register/complete` endpoints, `otp.py`, SMTP sender, and the
   register page. `.env` SMTP creds. (No open request endpoint.)
4. **Remember-me** — persistent token store + rotation + cookie.
5. **Admin polish & hardening** — `users` command, rate-limiting, docs, reset (opt).

## Confirmed decisions

1. **Browser-side SRP-6a** — password stays in the browser; complexity enforced
   client-side; server stores only `{salt, verifier}`.
2. **Invite-only registration** — accounts created only via `users add`, which emails
   an OTP invite; the user always sets their own password in the browser (the shell
   never sets one). No open request endpoint.
3. **Lifetimes** — session **12 h**, remember-me **30 d**, OTP **10 min**.
