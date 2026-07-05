# TLS, authentication & authorization for `solver-web`

This guide describes how `solver-web` is served securely and who is allowed to do
what once connected. It is both the design reference and the operational runbook.

## What this protects

`GET /ws` hands a browser a full interactive `solver` shell on a PTY, and the
`POST /<n>/…` routes write files and run commands — arbitrary remote code
execution as the repo owner. Three layers guard that surface, each answering a
different question:

- **TLS** (Caddy) encrypts the channel and presents a browser-trusted
  certificate. It authenticates nobody — it only secures the transport.
- **Authentication** (`solver/web/auth/`) is the access gate: it establishes *who*
  the caller is. It lives in the aiohttp app, not in Caddy, which stays a pure TLS
  reverse proxy.
- **Authorization** (`solver/commands.csv` and the shell) decides *which commands*
  an authenticated identity may run — see [Part 3](#part-3--command-authorization).

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

---

# Part 1 — TLS (Caddy + acme.sh, DNS-01)

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
the **username** and the **token**; both go in the project `.env` (below), and
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
project `.env` (the same file that holds `ANTHROPIC_API_KEY`):

| provider (arg) | acme.sh hook | credentials in `.env` |
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
access; authentication and authorization are what make that access safe.

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

---

# Part 2 — Authentication (browser-side SRP-6a)

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

`profile` (`admin` / `user` / `guest`) drives command authorization — see Part 3.

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
  their own password in the browser.
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

---

# Part 3 — Command authorization

Authentication establishes *who* the shell runs as; authorization decides *which
commands* that identity may run. The shell is the same `solver` program everywhere,
so two complementary layers narrow it to the context:

| Layer | Question | Driven by | Enforced at |
|---|---|---|---|
| **Channel-based** | which command *modules* load at all | `solver/modules.csv` (`terminal` / `web` columns) | module import (`shell/loader.py`) |
| **User-based** | which loaded commands a *profile* may run | `solver/commands.csv` (`admin` / `user` / `guest` columns) | the `@command` decorator (`shell/command.py`) |

The layers compose. `modules.csv` decides what loads per channel — for example
`solver.utils.update_doc` is `web=False`, so `update-docs` never loads in a web
shell. `commands.csv` then applies per profile on top: the `users` command *does*
load in a web shell, but its row grants only `admin`, so only a web admin can run
it.

## Profiles

Every identity carries one **profile** — `admin`, `user`, or `guest`, in descending
privilege. It is resolved once at startup (`solver/utils/identity.py`) and exposed
as `config.user_profile`:

- **Web** — the SRP-authenticated email is looked up in `keys/.users.json` and its
  stored `profile` applies. The web tier vouches for the email — it ran the SRP
  handshake — when it forks the per-user shell with `SOLVER_USER=<email>`.
- **Local terminal** — with no identity configured, resolution falls through to the
  OS login name and grants **`admin`**: access to the checkout is itself the trust
  (the channel-based half of the model). A local operator may `export SOLVER_USER=…`
  to *drop* to a named account's lower profile, but cannot gain privilege that way.

An explicitly configured identity (via the environment, `keys/.user-email`, or
`.env`) that is not an enabled account in `.users.json` aborts startup with
`invalid user`.

## The policy file (`solver/commands.csv`)

It mirrors `modules.csv`: a `command` column followed by one boolean column per
profile, where a truthy cell grants that profile the command.

```csv
command,admin,user,guest
benchmark,True,True,
users,True,,
show,True,True,True
```

Semantics (`is_authorized` in `shell/command.py`):

- A command **listed** in the policy is allowed only for the profiles its row grants
  (`benchmark` → admin + user; `users` → admin only; `show` → everyone).
- A command **absent** from the policy is **admin-only** — a fail-safe default, so a
  freshly added command is never silently exposed to `user` or `guest` before it is
  added to `commands.csv`.

`update-docs` keeps `commands.csv` reconciled with the live registry: it appends new
commands with the default `admin` + `user` grant, drops rows for removed commands,
and preserves every existing grant verbatim.

## Enforcement (decoration time)

The check lives in the `@command` decorator. As each command module is imported,
`command()` derives the command name and calls `is_authorized(name)` against
`config.user_profile`. If the profile is not permitted, the command is simply **not
registered** — invisible to `?`/help and tab-completion, and `unknown command`
(exit `127`) if invoked. The function itself is returned unchanged, so it remains a
normal Python callable.

Because one shell process serves exactly one identity, the profile — and therefore
the registered command set — is fixed for the life of the process, and the policy is
read once and cached.

## Assigning a profile

`users add <email> [profile]` seeds the invite with the chosen profile (`admin` /
`user` / `guest`; default `user`). The profile is stored on the account and
preserved through registration and password resets:

```
users add alice@example.com          # a standard user
users add bob@example.com guest      # read-only browsing
users add carol@example.com admin    # full access
```

Per-command availability — both channel and profile — is listed in
[`commands-index.md`](commands-index.md).

---

## Config & secrets summary

`solver/config.py` (application config, **not** crypto):

```python
users_file:          root_dir / 'keys' / '.users.json'
pending_file:        root_dir / 'keys' / '.pending.json'
remember_file:       root_dir / 'keys' / '.remember.json'
session_secret_file: root_dir / 'keys' / '.session-secret'
base_url:            EULER_BASE_URL or 'https://euler.vikasmunshi.com'
server_port:         8080
```

`.env` keys: `NAMEDOTCOM_USERNAME` / `NAMEDOTCOM_TOKEN` (or the chosen DNS
provider's pair), `SMTP_ADDRESS`, `SMTP_APP_PASSWORD`, and optionally
`EULER_BASE_URL`. Every auth file is a dot-file, so `**/.*` in `.gitignore` covers
them all (`.users.json`, `.pending.json`, `.remember.json`, `.session-secret`,
`.server.crt`, `.server.key`) with no per-file entries.

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
3. `solver "users add you@example.com"` emails a 24 h secure link (or prints it when
   SMTP is unconfigured); opening it loads `/register?token=…`, and setting a
   policy-compliant password completes registration. Logging in at `/login` never
   places the password in a request body (browser-side SRP). A tampered or expired
   token shows an error and no form, and `/register` with no token is linked from
   nowhere.
4. From a LAN device, `curl -v https://euler.vikasmunshi.com/login` returns the login
   page over a valid, browser-trusted certificate, and an unauthenticated `curl` of a
   gated page redirects to `/login`.
5. After login, the `/ws` shell connects, and an unauthenticated WebSocket upgrade is
   rejected before a socket is handed out.
6. For public access, add the router forward and firewall rule, wire up DDNS, and
   re-test from outside the LAN.

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
- [RFC 5054 — SRP for TLS](https://datatracker.ietf.org/doc/html/rfc5054)
