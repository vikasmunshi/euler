# Access control — authentication & authorization

How the web server establishes **who** a caller is and **what** that identity may
do. It is one half of a matched pair: [secure-web-server.md](secure-web-server.md)
covers the transport and infrastructure (TLS edge, service isolation, egress) and
holds the authoritative design-decision log (DD-1…DD-9); this guide covers the
access layer that rides on it, implementing **DD-6** (auth state + admin plane),
**DD-7** (registration) and **DD-9** (identity + masquerade prevention).

Everything here lives in the aiohttp auth service under **`solver/web/auth/`**,
running as `euler-auth` from the `/opt/euler` venv. Login is browser-side SRP-6a —
the password never crosses the wire — and Caddy gates every request through the
service's `forward_auth` endpoint before it reaches any downstream service.

## 1 · Purpose & scope

Three concerns, cleanly separated:

- **Authentication** — proving identity. Browser-side SRP-6a for web requests, a
  one-time ticket for web shells, the checkout-owner uid for the local terminal.
- **Authorization** — what a proven identity may do. A single **profile**
  (`admin`/`user`/`guest`) drives command and route availability.
- **Administration** — minting invites and enabling/disabling accounts, over a
  sudo-gated local admin plane.

### The no-mixing rule

Web-auth material is **entirely separate** from the git-filter master key —
different package, different key files, no shared secrets.

| Subsystem | Purpose | Lives in | Key material |
|---|---|---|---|
| Web authentication | gate the web front end | `solver/web/auth/` | `/var/lib/euler-auth/{users,pending,remember}.json`, `session-secret` |
| Solution encryption | git clean/smudge of `solutions/private/` | `solver/crypto/` | `~/.euler/id`, `keys/enc-key.json` |

Web login gates *access* only. Decrypting private solutions flows through the
separate `~/.euler/id` path (see [gitfilter-guide.md](gitfilter-guide.md)), which
shares no key material with web auth. A web session never unlocks the master key.

## 2 · Threat model

The web server runs a `solver` shell for invited collaborators — code execution is
by design, so the invite list is the real trust boundary. This guide's job is to
make **identity unforgeable** and **administration privileged**; blast-radius
containment is [secure-web-server](secure-web-server.md)'s. The standing accepted
risks (login = host RCE; web auth = plaintext read of private solutions) and the
sound controls not to regress are in [security-notes.md](security-notes.md).

**Masquerade prevention** is the sharp edge (DD-9): no caller may become a user or
profile that is not theirs. The vectors and their guards:

| Vector | Guard |
|---|---|
| Browser sends its own `X-User`/`X-Profile` | Caddy strips inbound copies; only the `forward_auth` response headers are forwarded; app sockets are unreachable except via Caddy |
| Web user re-execs `solver` with a chosen `SOLVER_USER` | env is display-only; identity requires a single-use ticket; the local fallback refuses non-owner uids |
| Replaying another shell's credential from `/proc/*/environ` | tickets are single-use — already consumed by the victim's own startup |
| Bare `solver` as a service uid claiming admin | the admin fallback requires the checkout-owner uid |
| Minting a ticket from inside a PTY | minting demands a live session cookie the shell user does not hold |
| Admin-plane abuse | `0600` euler-auth-private socket, **sudo-gated**, root-only token, never routed by Caddy |

## 3 · Design principles

The authoritative rationale is the DD log in
[secure-web-server.md](secure-web-server.md); the essentials:

- **Zero-knowledge password (SRP-6a).** The server stores only `{salt, verifier}`
  and never sees the password; each side proves knowledge through a challenge /
  response, and the client verifies the server back (mutual `M2`).
- **Invite-only, two-channel registration** (DD-7). An admin mints an invite; the
  invitee proves live mailbox control (OTP) and accepts Terms before any password
  is set. Every secret is stored hashed; every step is single-use and time-boxed.
- **Three identity planes** (DD-9), each with an explicit voucher — web request
  (`forward_auth`), web shell (one-time ticket), local terminal (checkout-owner
  uid). No anonymous fallback.
- **Profile-driven authorization.** One profile per identity gates both shell
  commands and (Phase 5) web routes, from a single policy file.
- **Wheel-gated administration** (DD-6). The admin plane is reachable only by root
  via `sudo`; the operator's ordinary uid holds no admin capability.

## 4 · How authentication works

### 4.1 Registration & reset (DD-7)

Invite-only and two-channel. The same link→OTP→password pipeline serves password
**reset** (self-service via `/forgot`, skipping Terms); admins never reset
passwords. All state is in `/var/lib/euler-auth/pending.json`, keyed by
`hash(link-token)`, walking `invited → otp_sent → verified → (consumed)`:

1. **Invite** — an admin runs `users add <email> [profile]`; the service mints a
   pending record `{email, profile, kind=register, state=invited, expiry=+7d}` and
   emails `https://<FQDN>/register?token=<32-byte token>`. No user record exists
   yet.
2. **Open link** — `GET /register?token=…`. Valid + unexpired + `invited` renders
   the page: the email (read-only), the **Terms of Use** in a scroll box (the
   accept checkbox unlocks only at the end of the text), and "email me a code".
   Invalid/expired → a generic "link not valid" page (no enumeration).
3. **Accept Terms + request OTP** — `POST /register/otp` records the Terms
   acceptance, mints a **6-digit OTP** (`hash(otp)`, `otp_expiry=+10min`,
   `attempts=0`), moves to `otp_sent`, and emails it. Resends are capped.
4. **Verify OTP** — `POST /register/verify`. A match (unexpired, `attempts<5`) →
   `verified`; **5 failed tries invalidate the OTP** and a fresh one must be
   requested.
5. **Set password (SRP)** — the browser derives `{salt, verifier}` locally from a
   policy-compliant password (the server never sees it) and `POST
   /register/complete`. On a `verified` record this creates the `users.json` entry
   (with the recorded Terms acceptance), **consumes** the pending record, and lands
   on `/login` (no auto-login).

**Token vs OTP.** The link token (32 bytes, 7-day, one registration session) proves
possession of the invite; the OTP (6 digits, 10-min, 5 tries) proves *live* mailbox
control at completion time. Both are stored only as hashes and never logged.

**Self-service reset.** `/forgot` (enter email) → if the account exists and is
enabled, a `kind=reset` link is emailed → OTP → set-password, identical but Terms
are skipped. Responses are **generic regardless of whether the email exists**.
Completing a reset revokes every live session and remember-me token for the account.

### 4.2 Login handshake (SRP-6a, browser-side)

1. `POST /auth/challenge {email}` → the service loads `{salt, v}`, computes its
   ephemeral `B = k·v + gᵇ`, and replies `{salt, B}`. Unknown or disabled accounts
   get a **stable decoy** `salt`/`B` (never stored) so the response reveals nothing.
2. `POST /auth/verify {email, A, M1, remember}` → the server checks `M1`; on success
   it replies `{M2, email, profile}` and sets the session cookie (and, if
   `remember`, the remember-me cookie); on failure, a generic 401.
3. The browser verifies `M2` — mutual authentication — and is logged in.

The browser client (`web-content/assets/srp.js`) interoperates byte-for-byte with
`srp.py`: RFC 5054 2048-bit group, `g=2`, SHA-256, `PAD`-to-`|N|` on `A`/`B`/`S`.
It is cross-tested against the Python server (`tests/test_srp_interop.py`, needs
`make install-nodejs`).

### 4.3 Sessions & remember-me (DD-6)

- **Session** `solver_session`: an opaque token → in-memory `(email, profile,
  expiry)`, 12 h TTL, `Secure; HttpOnly; SameSite=Lax; Path=/`. Sessions are
  per-process — a service restart drops them all.
- **Remember-me** `solver_remember` (only when requested): a selector\:validator
  token whose server side (`selector → (email, HMAC(validator), expiry)`) lives in
  `remember.json` and survives restarts (30-day TTL). On a request with a valid
  remember cookie but no session, `POST /auth/resume` verifies it (constant-time),
  **rotates** the validator (one-time use), and opens a fresh session. Logout
  (`POST /auth/logout`) clears both cookies and deletes the server-side record.

### 4.4 The `forward_auth` endpoint

`GET /auth/check` is what Caddy calls on every gated request: a live session →
`200` with **`X-User`** (email) and **`X-Profile`** (from the user record); no
session → `401`. Caddy copies those two headers onto the proxied request and
**deletes any client-supplied copies first**, so downstream services trust them
because the socket is reachable only via Caddy (DD-1/DD-2). A `401` is turned into a
`302 /login` for browser navigations.

### 4.5 Identity resolution (three planes, DD-9)

`solver/utils/identity.py` resolves `(display, slug, profile)` **once** at startup,
with no anonymous fallback:

| Plane | Voucher | Mechanism |
|---|---|---|
| Web request | auth service | SRP session cookie → `forward_auth` → `X-User` + `X-Profile` |
| Web shell (PTY child) | auth service | **one-time shell ticket**, redeemed over `auth.sock` |
| Local terminal | the OS | `os.getuid()` **owns the repo checkout** → `admin` |

**The shell ticket.** Every web shell runs as the shared `euler-ws` uid, and
`/proc/<pid>/environ` is same-uid-readable — so nothing env-carried can be the
credential (a sibling shell could replay it). Instead: on WS attach the ws service
forwards the user's session cookie to `POST /shell-ticket`, which mints a
**single-use, 60-second** ticket bound to `(email, profile)`; the forked child
redeems it at startup (`POST /shell-ticket/redeem`), which consumes it and returns
the authoritative identity. Missing/expired/reused → the shell aborts. Minting needs
a live cookie the shell user does not hold; the `/shell-ticket*` endpoints are not
routed by Caddy (socket-peer only).

**Local terminal.** The admin fallback applies **only** when the process uid owns
the checkout (`os.getuid() == stat(root_dir).st_uid`) — physical/login access to the
checkout is the trust. Service uids never fall through to admin. The old
assume-an-identity path (`SOLVER_USER` / `keys/.user-email` / env verified against a
user DB) is gone; `SOLVER_USER` is display-only.

Resolution order: `SOLVER_TICKET` set → redeem (failure aborts); else owner uid →
`admin`; else `SystemExit`.

## 5 · How authorization works

The shell is the same `solver` program everywhere, narrowed to its context by two
composing layers:

| Layer | Question | Driven by | Enforced at |
|---|---|---|---|
| **Channel** | which command *modules* load at all | `solver/modules.csv` (`terminal` / `web` columns) | module import (`shell/loader.py`) |
| **Profile** | which loaded commands a profile may run | `solver/commands.csv` (`admin`/`user`/`guest`) | the `@register`/`@command` decorator (`shell/command.py`) |

`modules.csv` decides what loads per channel — e.g. `update-docs` is `web=False`, so
it never loads in a web shell; `users` is terminal-only. `commands.csv` then applies
per profile on top.

### Profiles

Every identity carries one profile — `admin`, `user`, `guest`, descending privilege
— resolved at startup (§4.5) and exposed as `config.user_profile`. Web identities
carry the profile stored on their `users.json` record; the local operator (checkout
owner) is `admin`.

### The policy file (`solver/commands.csv`)

A `command` column followed by one boolean column per profile:

```csv
command,admin,user,guest
benchmark,True,True,
users,True,,
show,True,True,True
```

Semantics (`is_authorized`, `shell/command.py`):

- A command **listed** is allowed only for the profiles its row grants.
- A command **absent** is **admin-only** — a fail-safe default, so a freshly added
  command is never silently exposed before it is added to `commands.csv`.

`update-docs` keeps `commands.csv` reconciled with the live registry (appends new
commands with the default `admin`+`user` grant, drops removed ones, preserves every
existing grant). Per-command availability is listed in
[commands-index.md](commands-index.md).

### Enforcement in the shell (decoration time)

As each command module is imported, the decorator derives the command name and calls
`is_authorized(name)` against `config.user_profile`. If the profile is not permitted,
the command is simply **not registered** — invisible to `?`/help and completion,
`unknown command` (exit 127) if invoked. One shell process serves exactly one
identity, so the registered set is fixed for the life of the process.

### Enforcement on web routes (Phase 5)

The content service (Phase 5) exposes some of the same power outside the shell — file
save/delete, lint, progress — acting directly on the solution tree. Those routes are
gated by the **same policy** via a `requires(<command>)` decorator keyed on the
requester's `X-Profile`, so `commands.csv` stays the single source of truth across
both surfaces. (The content service is not yet built; this is the contract it will
honour.)

## 6 · Administration (the `users` command)

Account administration is the **wheel-gated admin plane** (DD-6). The `users` shell
command re-executes the admin CLI (`solver.web.auth.admin`) under `sudo` — the admin
socket (`/run/euler-adm/auth-admin.sock`) is `0600` euler-auth-private and the
`X-Admin-Token` lives only in root-readable `/etc/euler/auth.env`, so an ordinary
operator process holds no admin capability. It is terminal-only (`modules.csv`) and
never routed through Caddy.

```bash
users list                                # accounts + pending invites (never secrets)
users add alice@example.com               # mint + email an invite (default profile: user)
users add bob@example.com guest           # read-only browsing
users add carol@example.com admin         # full access
users disable alice@example.com           # also kills live sessions + remember tokens
users enable  alice@example.com
users remove  alice@example.com           # delete the account and any pending invites
```

`add` only mints an emailed invite — the account record is created when the invitee
completes registration (§4.1), with the profile assigned here preserved through
registration. There is deliberately **no reset verb**: reset is self-service (§4.1).
Expect a `sudo` password prompt (cached per sudo's usual timestamp).

## 7 · Reference

### State (`/var/lib/euler-auth`, `euler-auth`-only `0600`)

| File | Purpose |
|---|---|
| `users.json` | SRP verifier DB: `{salt, verifier, profile, terms_version, terms_accepted_at, created, disabled}` per email. Never a password. |
| `pending.json` | in-flight invites/resets, keyed by `hash(link-token)` (DD-7 state machine). |
| `remember.json` | remember-me `selector → (email, HMAC(validator), expiry)`, rotated on use. |
| `session-secret` | 32-byte HMAC key for remember-me; created on first start. |

### Policy constants (`solver/web/auth/policy.py`)

| Constant | Value | Meaning |
|---|---|---|
| `SESSION_TTL_SECONDS` | 12 h | session lifetime (in-memory) |
| `REMEMBER_TTL_SECONDS` | 30 d | remember-me lifetime (rotated on use) |
| `CHALLENGE_TTL_SECONDS` | 120 s | pending SRP challenge hold |
| `MIN_PASSWORD_LENGTH` / classes | 16 / lower+upper+digit+special | password policy (client-enforced) |
| `INVITE_TTL_SECONDS` / `LINK_TOKEN_BYTES` | 7 d / 32 | emailed link validity / entropy |
| `OTP_DIGITS` / `OTP_TTL_SECONDS` / `OTP_MAX_ATTEMPTS` / `OTP_MAX_SENDS` | 6 / 10 min / 5 / 5 | one-time code |
| `TICKET_TTL_SECONDS` | 60 s | one-time shell ticket (DD-9) |
| `AUTH_RATE_MAX` / `AUTH_RATE_WINDOW_SECONDS` | 30 / 60 s | per-client rate limit on unauthenticated endpoints |

### Runtime config (`/etc/euler/auth.env`, `root:euler-auth 0640`)

`EULER_BASE_URL`, `EULER_ADMIN_TOKEN` (root-only), `TERMS_VERSION`,
`EULER_SMTP_RELAY`. Deployed from the authoring source `~/.euler/env` by
`scripts/setup/auth.sh`; the auth service never reads the full `~/.euler/env` (no
Anthropic key, no SMTP creds — mail goes through the loopback relay, DD-8).

## 8 · Verify

1. `solver "users add you@example.com"` emails a 7-day invite; opening it walks
   Terms (scroll-gated) → OTP → set-password and lands on `/login?registered=1`.
2. Signing in at `/login` never places the password in a request body (browser-side
   SRP); a tampered/expired token shows the generic page, and `/register` with no
   token is linked from nowhere.
3. An unauthenticated request to any gated path `302`s to `/login`; `/healthz` and
   `/assets/*` stay public.
4. `/forgot` for a nonexistent email returns the same generic "check your mailbox"
   page as a real one (no enumeration).
5. Masquerade: a request with a forged `X-User` header is ignored (Caddy strips it);
   a bare `solver` run as a non-owner uid with no ticket aborts at startup.
