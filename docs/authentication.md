# Web authentication for `solver-web` (browser-side SRP-6a)

This guide covers how `solver-web` establishes *who* a caller is. It is the middle
layer of a three-part story: [TLS](tls-guide.md) secures the transport (and is a
prerequisite — the auth cookies are `Secure`), and [authorization](authorization.md)
decides what an authenticated identity may do.

Authentication lives entirely in the aiohttp app under **`solver/web/auth/`**;
Caddy plays no part. Login is browser-side SRP-6a: the password never crosses the
wire, the server stores only a salt and a verifier, and each side proves knowledge
to the other through a challenge/response.

## Separation of concerns (the no-mixing rule)

Authentication material is entirely separate from the git-filter master key —
different package, different import path, different key files.

| Subsystem | Purpose | Lives in | Key material |
|---|---|---|---|
| Solution encryption | git clean/smudge of `solutions/private/` | `solver/crypto/` | `keys/.id`, `keys/enc-key.json` |
| Web authentication | gate the web front end | `solver/web/auth/` | `keys/.users.json`, `keys/.remember.json`, `keys/.pending.json`, `keys/.session-secret` |

Web login gates *access* only. Decrypting private solutions flows through the
separate `.id` / `.user-pass` path, which shares no key material with web auth.

## Modules (`solver/web/auth/`)

- `srp.py` — SRP-6a primitives (`SrpServer`, verifier/token helpers): RFC 5054
  2048-bit group, `g=2`, SHA-256, left-padded to `|N|`.
- `users.py` — `UserStore` over `keys/.users.json` (load/save/get/add/disable;
  atomic writes at `0600`).
- `pending.py` — the persistent pending-registration store over `keys/.pending.json`:
  mint, verify, and consume the high-entropy secure-link tokens (stored **hashed**)
  that authorize a registration or a password reset, each valid 24 h.
- `mail.py` — Gmail SMTP sender for the registration and reset links.
- `sessions.py` — in-memory session table.
- `remember.py` — persistent, rotating remember-me tokens (selector:validator).
- `ratelimit.py` — in-memory sliding-window rate limiter for the auth endpoints.
- `routes.py` — the aiohttp handlers, the `@web.middleware` gate, and `setup_auth`.
- `policy.py` — lifetimes, cookie names, and the password-complexity and link-TTL
  constants.
- `commands.py` — the `users` shell command for account administration.

## Data model

All auth key material lives in **dot-files** under `keys/`, so a single `**/.*`
rule in `.gitignore` keeps every one of them out of git with no per-file entries.
Each is written `0600`.

### `keys/.users.json`

Keyed by normalized email (lowercased and trimmed). `salt` and `verifier` are
absent until the user completes registration in the browser; an
invited-but-unregistered account has `disabled: true` and no verifier.

```json
{
  "version": "srp6a-sha256-2048",
  "users": {
    "user@example.com": {
      "salt": "<hex>",
      "verifier": "<hex>",
      "created": "<iso8601>",
      "disabled": false,
      "profile": "user"
    }
  }
}
```

`profile` (`admin` / `user` / `guest`) drives command and route authorization — see
[authorization](authorization.md).

### `keys/.pending.json`

The persistent registration / reset store. It holds the secure-link tokens and so
must survive restarts (a link is valid for 24 h). It is keyed by the token's hash,
never by the token itself:

```json
{
  "pending": {
    "<sha256(token)>": {
      "email": "user@example.com",
      "kind": "register",
      "expires": "<iso8601>"
    }
  }
}
```

`kind` is `register` or `reset`. A token is single-use — deleted when registration
or reset completes — and swept on expiry.

### `keys/.session-secret`

32 random bytes, generated and persisted on first run. The HMAC key for remember-me
tokens: an application secret, deliberately **not** part of `solver/crypto`.

### `keys/.remember.json`

The server side of the remember-me tokens (`selector → {email, HMAC(validator),
expires}`), so logins survive a restart.

### In-memory (per-process) state

- **Pending SRP logins**: `email → {b, B, expires}`, the ephemeral values held
  between the challenge and verify steps (`CHALLENGE_TTL_SECONDS` = 120 s).
- **Sessions**: `token → {email, expires}`. A restart clears them all; remember-me
  cookies restore the affected users on their next request.

## Policy constants (`policy.py`)

| Constant | Value | Meaning |
|---|---|---|
| `SESSION_COOKIE` | `solver_session` | short-lived session cookie |
| `SESSION_TTL_SECONDS` | 12 h | session lifetime |
| `REMEMBER_COOKIE` | `solver_remember` | rotating remember-me token |
| `REMEMBER_TTL_SECONDS` | 30 d | remember-me lifetime (refreshed on use) |
| `CHALLENGE_TTL_SECONDS` | 120 s | pending SRP challenge hold |
| `MIN_PASSWORD_LENGTH` | 16 | minimum characters |
| `PASSWORD_REQUIRE_CLASSES` | lower + upper + digit + special | all four required |
| `REGISTRATION_TTL_SECONDS` | 24 h | validity of the emailed registration / reset link |
| `REGISTRATION_TOKEN_BYTES` | 32 | entropy of the secure-link token |
| `AUTH_RATE_MAX` / `AUTH_RATE_WINDOW_SECONDS` | 30 / 60 s | per-IP rate limit on the unauthenticated auth/register endpoints |

**Password policy: at least 16 characters, including one lowercase letter, one
uppercase letter, one digit, and one special character.** Since the server never
sees the password (browser-side SRP), the policy is enforced **client-side**,
before the verifier is computed. The set-password screen also offers a one-click
generator (below) that always produces a compliant password. For a small, trusted
user set this is sufficient — a user only ever weakens their own account.

## Registration (invite-only, secure link)

There is no public "request an account" endpoint, and the register page is linked
from nowhere in the app: it is reachable only through a token in an emailed link.
An admin authorizes an email from the shell with **`users add <email>`**, which:

1. Creates the account in `.users.json` with **`disabled: true`** and no verifier.
2. Mints a high-entropy registration token (`REGISTRATION_TOKEN_BYTES`) and stores
   its **hash** in `.pending.json` as `{email, kind: register, expires=+24 h}`.
3. Emails the user a **secure link** —
   `https://euler.vikasmunshi.com/register?token=<token>`, valid 24 h — or prints
   the link on the console when SMTP is unconfigured.

The invited user opens the link and completes registration in the browser:

1. `GET /register?token=…` serves the register page (a public asset). The page
   `POST`s the token to **`/register/validate`** `{token}`, which confirms the hash
   exists and is unexpired and returns `{email}` for display (a generic 400
   otherwise) — an invalid or stale link shows an error and no form.
2. The user chooses a password that satisfies the complexity policy (or clicks the
   generator); the browser generates a salt and computes the SRP verifier locally.
3. `POST /register/complete` `{token, salt, verifier}` re-validates the token,
   persists `{salt, verifier}` to `.users.json`, flips the account to
   **`disabled: false`**, and **consumes** the token. The password never crosses
   the wire.

**Password reset** (`users reset <email>`) reuses this mechanism with `kind: reset`
— the same 24 h secure link and set-password page — and replaces the verifier of an
existing account.

**Gmail delivery** (`mail.py`): `smtp.gmail.com:587` over STARTTLS, authenticated
with the Gmail address and an **App Password**. Credentials come from `.env`
(`SMTP_ADDRESS`, `SMTP_APP_PASSWORD`); `EULER_BASE_URL` (default
`https://euler.vikasmunshi.com`) forms the link's base URL. Sending runs via
`smtplib` in `run_in_executor`.

## Login flow (SRP-6a, browser-side)

1. `POST /auth/challenge` `{email, A}` looks up `{salt, v}`, computes `b` and
   `B = k·v + g^b`, stashes the ephemeral `{b, B}`, and replies `{salt, B}`. Unknown
   emails receive a stable decoy `salt`/`B` to prevent user enumeration.
2. `POST /auth/verify` `{email, A, M1}`: `SrpServer` computes `u, S, K` and checks
   `M1`; on success it replies `{M2}` and opens a session cookie, and on failure a
   generic 401.
3. The browser verifies `M2` (mutual authentication) and is then logged in.

`remember=true` on step 2 additionally sets the persistent remember-me cookie.

## Sessions & remember-me

- **Session cookie** `solver_session`: an opaque token mapping to in-memory
  `{email, expires}`, 12 h TTL, with attributes `Secure; HttpOnly; SameSite=Strict;
  Path=/`.
- **Remember-me cookie** `solver_remember` (only when requested): a
  selector:validator token whose server side (`selector → {email, HMAC(validator),
  expires}`) lives in `keys/.remember.json` and survives restarts. Long TTL (30 d),
  same cookie attributes. On a request with no valid session but a valid remember
  cookie, the server verifies it (constant-time), **rotates** the validator
  (one-time use), and opens a fresh session. Logout clears both cookies and deletes
  the server-side remember record.

## Middleware (the gate)

`auth_middleware` (`routes.py`, wired by `setup_auth`) admits only the public
paths: `/login`, `/logout`, `/auth/challenge`, `/auth/verify`, `/register`,
`/register/validate`, `/register/complete`, and the login/register static assets
(`login.*`, `register.*`, `srp-client.js`, favicons). `/register` is useful only
with a valid `?token=…`, and nothing in the app links to it.

Everything else — pages, the viewer, the edit/cmd routes, the self-service password
endpoints (`/whoami`, `/password`, `/password/change`), and the **`/ws` PTY** —
requires a valid session (or a remember cookie promoted to one). For `/ws`, the
cookie is checked **before** `ws.prepare()`, so an unauthenticated client never
receives a socket. Browser navigations without a session redirect to
`/login?next=…` (sanitized to a same-site path); programmatic fetches get `401`.
The per-IP rate limiter guards the unauthenticated auth/register endpoints (429 on
breach), and gated page responses carry `no-store` so a cached page redirects to
login after logout.

Authenticating a request establishes the identity; deciding what that identity may
*do* — which commands and mutating routes it may use — is the job of
[authorization](authorization.md).

## Frontend (`solver/web-content/`)

- `login/` — `login.html` / `login.css` / `login.js`: the email + password form; on
  submit it runs the SRP client (challenge → verify) and redirects to `next`.
- `register/` — the set-password page, opened only from the emailed link. On load it
  reads `?token`, validates it via `/register/validate` (showing the target email or
  an "invalid/expired link" message), then presents the password pane. That pane
  enforces the complexity policy live (≥16 chars; lower + upper + digit + special),
  computes `{salt, verifier}` locally, and `POST`s `/register/complete`. It includes
  the password generator (below). The same page serves password resets.
- `password/` — self-service password change for a signed-in user, with the same
  complexity enforcement and generator.
- **Password generator** (shared by the register and password panes): **Generate**
  produces a random password that always satisfies the policy (≥16 chars drawn from
  all four classes, via `crypto.getRandomValues`); **Copy** places it on the
  clipboard, and **Use** fills the password field(s), so the user adopts it without
  typing.
- `srp-client/srp-client.js` — browser SRP-6a, interoperable with `srp.py`: the same
  `H` (SHA-256), `k=H(N|PAD(g))`, `x=H(salt|H(email|":"|password))`, `M1`/`M2`
  construction, and `PAD`-to-`|N|` on `A`/`B`/`S`. It uses BigInt for modpow and
  WebCrypto for SHA-256, and is cross-tested against vectors generated by `srp.py`.

## Shell commands (admin)

The `users` command group (`commands.py`) administers accounts outside the web
flow:

- `users list` — emails with their created/disabled state (never secrets).
- `users add <email> [profile]` — the invite-only registration trigger: creates a
  `disabled`, password-less account with the given profile, mints a 24 h
  registration token, and emails the secure link. The invited user always chooses
  their own password in the browser. The `profile` argument feeds
  [authorization](authorization.md).
- `users reset <email>` — mints a 24 h reset link for an existing account (the same
  secure-link mechanism, `kind: reset`).
- `users disable <email>` / `users enable <email>` / `users remove <email>`.

## Security considerations

- **Invite-only registration** — no public request endpoint, and nothing links to
  the register page. Accounts are authorized one email at a time via `users add`.
  This is the primary gate on the RCE shell.
- **Secure links** — the registration/reset token carries `REGISTRATION_TOKEN_BYTES`
  of entropy, is stored **hashed** in `.pending.json`, expires after 24 h, and is
  **single-use**. Possession of the emailed link is the sole proof of control of
  the address.
- **User enumeration** — neutral responses from `/register/validate`, and a decoy
  `salt`/`B` from `/auth/challenge`.
- **Brute force** — per-IP rate limiting on the auth/register endpoints
  (`ratelimit.py`, 429); guessing a 32-byte token is infeasible.
- **Timing** — constant-time comparison for token hashes, `M1`/`M2`, and remember
  validators.
- **Cookies** — `Secure; HttpOnly; SameSite=Strict`; remember tokens rotate on each
  use and are server-side revocable.
- **CSRF** — `SameSite=Strict` covers the main risk; state-changing POSTs are
  same-origin fetches from our own pages.
- **Headers** — `nosniff`, frame-`DENY`, and `no-referrer` on responses; gated pages
  carry `no-store`.
- **No secrets in logs**; `.users.json` / `.pending.json` / `.remember.json` /
  `.session-secret` are all `0600`.

## Configuration summary

`solver/config.py` (application config, **not** crypto):

```python
users_file:          root_dir / 'keys' / '.users.json'
pending_file:        root_dir / 'keys' / '.pending.json'
remember_file:       root_dir / 'keys' / '.remember.json'
session_secret_file: root_dir / 'keys' / '.session-secret'
base_url:            EULER_BASE_URL or 'https://euler.vikasmunshi.com'
server_port:         8080
```

`.env` keys: `SMTP_ADDRESS`, `SMTP_APP_PASSWORD` (Gmail App Password), and optionally
`EULER_BASE_URL`. Every auth file is a dot-file, so `**/.*` in `.gitignore` covers
them all (`.users.json`, `.pending.json`, `.remember.json`, `.session-secret`) with
no per-file entries.

## Verify

1. `solver "users add you@example.com"` emails a 24 h secure link (or prints it when
   SMTP is unconfigured); opening it loads `/register?token=…`, and setting a
   policy-compliant password completes registration.
2. Logging in at `/login` never places the password in a request body (browser-side
   SRP). A tampered or expired token shows an error and no form, and `/register` with
   no token is linked from nowhere.
3. An unauthenticated `curl` of a gated page redirects to `/login`; after login, the
   `/ws` shell connects and an unauthenticated WebSocket upgrade is rejected before a
   socket is handed out.
