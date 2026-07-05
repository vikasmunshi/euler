# TLS & authentication for `solver-web`

> **Status: implemented.** Both layers are in the tree and working:
> TLS termination via **Caddy + acme.sh** (DNS-01), and web authentication via
> **browser-side SRP-6a** in the aiohttp app (`solver/web/auth/`). This guide is
> the design reference and the operational runbook.

## What this protects & why both layers exist

`GET /ws` hands any connected browser a full interactive `solver` shell on a PTY,
and the `POST /<n>/…` routes write files and run commands — that is **arbitrary
remote code execution as the repo owner.** Two independent layers guard it:

- **TLS** (Caddy) encrypts the channel and gives a browser-trusted certificate.
  It authenticates *nobody*.
- **Authentication** (aiohttp `solver/web/auth/`) is the access gate. It sits in
  the app, not in Caddy — Caddy stays a pure TLS reverse proxy.
- **Authorization** (`solver/commands.csv` + the shell) narrows *which commands* a
  signed-in identity may run, by profile — see [Part 3](#part-3--command-authorization).


## Architecture

```
Internet / LAN
   │  https :443
   ▼  Router : forward TCP 443 → <host ip> TCP 443
   ▼  System Firewall(s): inbound allow TCP 443
   ▼
   Caddy  :443  ── terminates TLS ──►  reverse_proxy  ──►  aiohttp 127.0.0.1:8080
          ▲   loads keys/.server.crt + keys/.server.key                 │  SRP auth gate
          │   reload on renewal                                         │  (solver/web/auth/)
 acme.sh ─┘   DNS-01 ──► Provider API (writes _acme-challenge TXT)  ──► Let's Encrypt

   DDNS updater ──► Provider API (keeps euler A → current public IP)
```

Port 8080 is bound to loopback (`solver/web/cli.py` binds `host='127.0.0.1'`) and
is not reachable from the LAN; only Caddy on :443 is served. DNS-01 needs no
inbound port for the challenge, so nothing listens on :80.

---

# Part 1 — TLS (Caddy + acme.sh, DNS-01)

Serve the aiohttp front end at `https://euler.vikasmunshi.com` with a Let's
Encrypt certificate that auto-renews. `solver-web` is unchanged except for its
loopback bind; **Caddy** terminates TLS and reverse-proxies to aiohttp, loading a
cert that **acme.sh** issues and renews via the name.com DNS-01 challenge.

**Why acme.sh and not Caddy's own ACME:** the `caddy-dns/namedotcom` plugin is
unmaintained and no longer builds against current Caddy (the download service
returns HTTP 400 for it), so stock Caddy cannot perform the name.com DNS-01
challenge itself. Certificate issuance is delegated to **acme.sh**, whose
`dns_namecom` client works with the name.com API; **stock** Caddy just loads the
resulting cert. This keeps the DNS-01 benefit (a real cert with no inbound port
open) without the broken plugin.

## The DNS API token

One name.com API token drives two things, both **outside** Caddy:

| Purpose | Record | Driven by | When |
|---|---|---|---|
| **DNS-01 challenge** | `_acme-challenge.euler.vikasmunshi.com` TXT | **acme.sh** (`dns_namecom`) | at issue/renewal; created then deleted |
| **Dynamic DNS** | `euler.vikasmunshi.com` A | **external updater** | only when public |

### 1. Create the token

name.com account → **API** (api.name.com) → create a token. Note the **username**
and the **token**; they go in the project `.env` (below) and acme.sh caches them
for renewals.

### 2. Install Caddy (stock)

```bash
scripts/setup/caddy.sh install euler.vikasmunshi.com   # also: update | service | uninstall | status
```

This installs stock Caddy from the official apt repo, **stops/disables the default
`caddy.service`** so it does not clash, **generates the `Caddyfile`** for the given
hostname, and installs the **`caddy-euler.service`** unit — enabled immediately and
started once the cert + Caddyfile are in place. No DNS plugin is needed.

The hostname may be passed to `install`, taken from `$EULER_TLS_DOMAIN` (shared
with acme.sh), or entered at a prompt. The `Caddyfile` is gitignored (it carries
the deployment hostname) and rewritten on each `install`; a repeated `install`
with no hostname leaves an existing `Caddyfile` untouched.

### 3. Issue the certificate with acme.sh

`acme.sh issue` requires the `Caddyfile` (its reload command points at it), so run
step 2 first. The DNS provider is selectable — pass it to `issue`/`renew` or set
`$EULER_TLS_DNS_PROVIDER` (default `namecom`). Add that provider's credentials to
the project `.env` (the same file that holds `ANTHROPIC_API_KEY`):

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
`keys/.server.crt` and the key to `keys/.server.key` (mode 600; both dotfiles,
gitignored by `**/.*`), and registers a reload command so Caddy picks up the cert
now and on every renewal. acme.sh's cron auto-renews thereafter
(`scripts/setup/acme.sh renew [provider]` forces one).

- The default reload command is `caddy reload --config <root>/Caddyfile` (Caddy's
  admin API, no sudo); override with `EULER_TLS_RELOAD_CMD`. Override the
  domain/email with `EULER_TLS_DOMAIN` / `EULER_TLS_EMAIL`.
- On the very first `issue`, Caddy may not be running yet, so the reload is a
  harmless no-op — the cert still deploys; start Caddy (§4) and it loads it.

### 4. The Caddyfile & service

`caddy.sh install` **generates** this `Caddyfile` for your hostname (gitignored,
not tracked). Caddy loads the acme.sh cert and does **no** ACME itself;
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

- Cert paths are **relative to Caddy's working directory** — the systemd unit sets
  `WorkingDirectory` to the repo root, so there are no machine-specific paths. (For
  a manual `caddy run`, `cd` to the repo root first.)
- `reverse_proxy` upgrades WebSocket connections automatically, so `/ws` works.
- Validate from the repo root: `caddy validate --config Caddyfile`.

acme.sh deploys the cert as the repo owner into `keys/`; the packaged Caddy runs
as the unprivileged `caddy` user, which cannot read files under your home. So the
generated **`caddy-euler.service`** runs Caddy **as the repo owner** — `User`/`Group`
are the checkout's owner, `WorkingDirectory` is the repo root, binary + config
paths are derived (`CAP_NET_BIND_SERVICE` lets it bind :443 without root). If the
cert was not present at install time, the unit is enabled but not started; start it
once §3 has issued the cert:

```bash
scripts/setup/caddy.sh service     # validates the Caddyfile, then starts the unit
systemctl status caddy-euler
```

Named `caddy-euler` to avoid colliding with the default `caddy.service`; do **not**
re-enable that default. The acme.sh `--reloadcmd` reloads this running instance on
every renewal.

## Going public (router + firewall)

Only needed when exposing the server beyond the LAN — auth now guards it, so this
is a deliberate choice rather than a blocker.

### Router

- Port-forward **TCP 443 → the host's LAN IP** (no port 80 needed for DNS-01).
- Give this machine a **DHCP reservation** so its LAN IP does not drift.

### System Firewalls (Windows Hyper-V Firewall)

For this setup, mirrored-mode WSL2 filters inbound traffic via the Hyper-V Firewall.
From an **elevated PowerShell on Windows**:

```powershell
New-NetFirewallHyperVRule -Name "WSL-Caddy-443" -DisplayName "WSL Caddy HTTPS" `
  -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' `
  -Protocol TCP -LocalPorts 443 -Action Allow
```

Confirm the VMCreatorId with `Get-NetFirewallHyperVVMCreator`; add specific
per-port rules only. Requires `[wsl2] firewall=true` in `.wslconfig` (default).

### Dynamic DNS

The A record must track the ISP's changing public IP. Caddy's DDNS is unavailable
(same broken name.com plugin), so use a **small updater in WSL** on a systemd
timer / cron: read the public IP (`curl https://api.ipify.org`) and `PUT` the
name.com A record when it changes. (Router DynDNS is awkward with name.com's REST
API and not recommended.)

---

# Part 2 — Authentication (browser-side SRP-6a)

Authentication lives entirely in the aiohttp app under **`solver/web/auth/`** —
Caddy is not involved. Login is **true browser-side SRP-6a**: the password never
crosses the wire; the server stores only a salt + verifier and proves mutual
knowledge via challenge/response.

## Separation of concerns (the no-mixing rule)

SRP/auth material is wholly separate from the git-filter master key — different
package, different import path, different key files.

| Subsystem | Purpose | Lives in | Key material |
|---|---|---|---|
| Solution encryption | git clean/smudge of `solutions/private/` | `solver/crypto/` | `keys/.id`, `keys/enc-key.json` |
| Web authentication | gate the web front end | `solver/web/auth/` | `keys/.users.json`, `keys/.remember.json`, `keys/.pending.json`, `keys/.session-secret` |

Web login gates *access only*; decrypting private solutions still flows through the
existing `.id` / `.user-pass` path, untouched and independent.

## Modules (`solver/web/auth/`)

- `srp.py` — SRP-6a primitives (`SrpServer`, verifier/token helpers). RFC 5054
  2048-bit, `g=2`, SHA-256, left-pad to `|N|`.
- `users.py` — `UserStore` over `keys/.users.json` (load/save/get/add/disable,
  atomic write, `0600`).
- `pending.py` — persistent pending-registration store over `keys/.pending.json`:
  mint / verify / consume the high-entropy secure-link tokens (stored **hashed** at
  rest) that authorize a registration or a password reset, each valid 24 h.
- `mail.py` — Gmail SMTP sender for the registration / reset link.
- `sessions.py` — in-memory session table.
- `remember.py` — persistent rotating remember-me tokens (selector:validator).
- `ratelimit.py` — in-memory sliding-window rate limiter for the auth endpoints.
- `routes.py` — the aiohttp handlers + the `@web.middleware` gate + `setup_auth`.
- `policy.py` — lifetimes, cookie names, password-complexity + link-TTL constants.
- `commands.py` — the `users` shell command (admin management).

## Data model

All auth key material is stored in **dot-files** under `keys/`, so a single
`**/.*` rule in `.gitignore` keeps every one of them out of git — no per-file
entries needed. Each is written `0600`.

### `keys/.users.json`

Keyed by normalized email (lowercased, trimmed). `verifier`/`salt` are absent
until the user completes registration in the browser; an invited-but-unregistered
account has `disabled: true` and no verifier.

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

### `keys/.pending.json`

The persistent registration / reset store — it holds the secure-link tokens, so it
**must survive restarts** (the link is valid for 24 h). Keyed by the token's hash,
never the token itself:

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

`kind` is `register` or `reset`. Tokens are single-use — consumed (deleted) when
registration/reset completes — and swept on expiry.

### `keys/.session-secret`

32 random bytes, generated + persisted on first run. HMAC key for remember-me
tokens. An app secret — **not** in `solver/crypto`.

### `keys/.remember.json`

Server side of the remember-me tokens (`selector → {email, HMAC(validator),
expires}`), so they survive restarts.

### In-memory (per-process) state

- **Pending SRP logins**: `email → {b, B, expires}` ephemeral values between the
  challenge and verify steps (`CHALLENGE_TTL_SECONDS` = 120 s).
- **Sessions**: `token → {email, expires}` (a restart logs everyone out —
  remember-me restores them).

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
| `REGISTRATION_TOKEN_BYTES` | 32 | entropy of the secure link token |
| `AUTH_RATE_MAX` / `AUTH_RATE_WINDOW_SECONDS` | 30 / 60 s | per-IP rate limit on unauthenticated auth/register endpoints |

**Password policy: minimum 16 characters, with at least one lowercase letter, one
uppercase letter, one digit, and one special character.** Because the server never
sees the password (browser-side SRP), the policy is enforced **client-side**, in the
browser, before the verifier is computed. The set-password screen also offers a
one-click generator (below) that always produces a compliant password, so a user
never has to hand-craft one. For a small, trusted user set this is sufficient — a
user only weakens their own account.

## Registration (invite-only, secure link)

There is **no** public "request an account" endpoint, and the register page is
**not linked from anywhere** in the app — it is reached only through a token in an
emailed link. An admin authorizes an email from the shell with
**`users add <email>`**, which:

1. Creates the account in `.users.json` with **`disabled: true`** and no verifier.
2. Mints a high-entropy registration token (`REGISTRATION_TOKEN_BYTES`), stores its
   **hash** in `.pending.json` as `{email, kind: register, expires=+24 h}`, and
3. Emails the user a **secure link** — `https://euler.vikasmunshi.com/register?token=<token>` —
   valid for 24 h (falling back to printing the link on the console if SMTP is
   unconfigured).

The invited user opens the link and completes registration in the browser:

1. `GET /register?token=…` serves the register page (a public asset). The page
   `POST`s the token to **`/register/validate`** `{token}`, which checks the hash
   exists and is unexpired and returns `{email}` to display (generic 400 otherwise) —
   an invalid or stale link shows an error and no form.
2. The user sets a password that satisfies the **complexity policy** (or clicks the
   generator); the browser generates a salt and computes the SRP verifier locally.
3. `POST /register/complete` `{token, salt, verifier}` → the server re-validates the
   token, persists `{salt, verifier}` to `.users.json`, flips the account to
   **`disabled: false`**, and **consumes** the token (single-use). Password never
   crosses the wire.

**Password reset** (`users reset <email>`) reuses exactly this mechanism with
`kind: reset` — same 24 h secure link, same set-password page, replacing the
verifier of an existing account.

**Gmail sending** (`mail.py`): `smtp.gmail.com:587` STARTTLS, login with the Gmail
address + an **App Password**. Creds from `.env`: `SMTP_ADDRESS`,
`SMTP_APP_PASSWORD`. `EULER_BASE_URL` (default `https://euler.vikasmunshi.com`)
builds the link's base URL. Sent via `smtplib` in `run_in_executor`.

## Login flow (SRP-6a, browser-side)

1. `POST /auth/challenge` `{email, A}` → look up `{salt, v}`; compute `b`,
   `B = k·v + g^b`; stash ephemeral `{b, B}`; reply `{salt, B}`. (Decoy salt/`B`
   for unknown emails to avoid user enumeration.)
2. `POST /auth/verify` `{email, A, M1}` → `SrpServer` computes `u, S, K`, checks
   `M1`; on success reply `{M2}` and open a session cookie; on failure, generic 401.
3. The browser verifies `M2` (mutual auth), then it is logged in.

`remember=true` on step 2 additionally sets the persistent remember-me cookie.

## Sessions & remember-me

- **Session cookie** `solver_session`: opaque token → in-memory `{email, expires}`,
  12 h TTL. Attributes: `Secure; HttpOnly; SameSite=Strict; Path=/`.
- **Remember-me cookie** `solver_remember` (only when requested): selector:validator
  pattern; the server stores `selector → {email, HMAC(validator), expires}` in
  `keys/.remember.json` so it survives restarts. Long TTL (30 d), same attributes. On
  a request with no valid session but a valid remember cookie: verify
  (constant-time), **rotate** the validator (one-time-use), and open a fresh
  session. Logout clears both cookies and deletes the server-side remember record.

## Middleware (the gate)

`auth_middleware` (`routes.py`, wired by `setup_auth`) allows only the public
paths: `/login`, `/logout`, `/auth/challenge`, `/auth/verify`, `/register`,
`/register/validate`, `/register/complete`, and the login/register static assets
(`login.*`, `register.*`, `srp-client.js`, favicons). `/register` is reachable only
with a valid `?token=…`; it is linked from nowhere in the app.

Everything else — pages, viewer, edit/cmd routes, self-service password endpoints
(`/whoami`, `/password`, `/password/change`), and the **`/ws` PTY** — requires a
valid session (or a remember cookie promoted to one). For `/ws`, the cookie is
checked **before** `ws.prepare()` so an unauthenticated client never gets a socket.
Browser navigations without a session redirect to `/login?next=…` (sanitized to a
same-site path); programmatic fetches get `401`. The per-IP rate limiter guards the
unauthenticated auth/register endpoints (429 on breach). Gated page responses are
sent `no-store` so a cached page redirects to login after logout.

## Frontend (`solver/web-content/`)

- `login/` — `login.html` / `login.css` / `login.js`: email + password form; on
  submit runs the SRP client (challenge → verify), then redirects to `next`.
- `register/` — the set-password page, opened only from the emailed link. On load it
  reads `?token`, validates it via `/register/validate` (showing the target email or
  an "invalid/expired link" error), then presents the password pane. That pane
  enforces the complexity policy (≥16 chars; lower + upper + digit + special) live,
  computes `{salt, verifier}` locally, and `POST`s `/register/complete`. It includes
  the **password generator** (below). Reused for password reset (`kind: reset`).
- `password/` — self-service password change for a signed-in user; same complexity
  enforcement and the same generator.
- **Password generator** (shared JS used by the register and password panes): a
  "Generate" button produces a random password that always satisfies the policy
  (≥16 chars drawn from all four classes, cryptographically random via
  `crypto.getRandomValues`); a **Copy** button puts it on the clipboard and a
  **Use** button fills the password field(s), so the user can adopt it without
  typing.
- `srp-client/srp-client.js` — browser SRP-6a, **interoperable** with `srp.py`: same
  `H` (SHA-256), same `k=H(N|PAD(g))`, same `x=H(salt|H(email|":"|password))`, same
  `M1/M2` construction, and the same `PAD`-to-`|N|` on `A/B/S`. BigInt modpow +
  WebCrypto for SHA-256, cross-tested against vectors generated by `srp.py`.

## Shell commands (admin)

The `users` command group (`commands.py`) manages accounts without the web flow:

- `users list` — emails + created/disabled state (never secrets).
- `users add <email>` — **the** registration trigger (invite-only): create a
  `disabled`, password-less account, mint a 24 h registration token, and email the
  secure link. The invited user always chooses their own password in the browser.
- `users reset <email>` — mint a 24 h reset link for an existing account (same
  secure-link mechanism, `kind: reset`).
- `users disable <email>` / `users enable <email>` / `users remove <email>`.

## Security considerations

- **Invite-only registration** — no public request endpoint and the register page
  is linked from nowhere; accounts are authorized one email at a time via
  `users add`. This is the primary gate on the RCE shell.
- **Secure links** — the registration/reset token carries
  `REGISTRATION_TOKEN_BYTES` of entropy, is stored **hashed** in `.pending.json`,
  expires after 24 h, and is **single-use** (consumed on completion). Possession of
  the emailed link is the sole proof of control of the address.
- **User enumeration** — neutral responses on `/register/validate`, decoy salt/`B`
  on `/auth/challenge`.
- **Brute force** — per-IP rate-limiting on the auth/register endpoints
  (`ratelimit.py`, 429); guessing a token is infeasible at 32 bytes of entropy.
- **Timing** — constant-time compares for token hashes, `M1`/`M2`, remember
  validators.
- **Cookies** — `Secure; HttpOnly; SameSite=Strict`; remember tokens single-use
  (rotate on each use), server-side revocable.
- **CSRF** — `SameSite=Strict` covers the main risk; state-changing POSTs are
  same-origin fetches from our pages.
- **Headers** — `nosniff`, frame-`DENY`, `no-referrer` on responses; gated pages
  `no-store`.
- **No secrets in logs**; `.users.json` / `.pending.json` / `.remember.json` /
  `.session-secret` at `0600`.

---

# Part 3 — Command authorization

Authentication proves *who* the shell is running as; **authorization** decides
*which commands* that identity may run. The shell is the same `solver` program
everywhere, so a single mechanism narrows it per context. There are two
independent, complementary layers:

| Layer | Question | Driven by | Enforced at |
|---|---|---|---|
| **Channel-based** | which commands' *modules* load at all | `solver/modules.csv` (`terminal` / `web` columns) | module import (`shell/loader.py`) |
| **User-based** | which loaded commands a *profile* may run | `solver/commands.csv` (`admin` / `user` / `guest` columns) | the `@command` decorator (`shell/command.py`) |

Channel-based gating is the pre-existing `modules.csv`: e.g. `solver.web.auth.commands`
and `solver.utils.update_doc` are `web=False`, so the `users` and `update-docs`
commands don't even load in a web shell. User-based gating is the new
`commands.csv`, applied on top.

## Profiles

Every identity carries one **profile** — `admin`, `user`, or `guest` — in
descending privilege. It is resolved once at startup (`solver/utils/identity.py`)
and exposed as `config.user_profile`:

- **Web** — the SRP-authenticated email is looked up in `keys/.users.json`; its
  stored `profile` is used. The web tier vouches for the email (it ran the SRP
  handshake) when it forks the per-user shell with `SOLVER_USER=<email>`.
- **Local terminal** — with no identity configured, the shell falls through to the
  OS login name and is granted **`admin`**: access to the checkout *is* the trust
  (the channel-based half of the model). A local operator may `export SOLVER_USER=…`
  to *drop* to a named account's lower profile, but cannot thereby gain privilege.

An explicitly configured identity (env / `keys/.user-email` / `.env`) that is not
an enabled account in `.users.json` aborts startup (`invalid user`).

## The policy file (`solver/commands.csv`)

Mirrors `modules.csv`: a `command` column then one boolean column per profile. A
truthy cell grants that profile the command.

```csv
command,admin,user,guest
benchmark,True,True,
users,True,,
show,True,True,True
```

Semantics (`is_authorized` in `shell/command.py`):

- A command **listed** in the policy is allowed only for the profiles its row
  grants (`benchmark` → admin + user; `users` → admin only; `show` → everyone).
- A command **absent** from the policy is **admin-only** — a fail-safe default, so
  a newly added command is never silently exposed to `user`/`guest` before it is
  added to `commands.csv`.

## Enforcement (decoration time)

The check lives in the `@command` decorator: as each command module is imported,
`command()` computes the command name and calls `is_authorized(cmd_name)` against
`config.user_profile`. If the profile is not permitted, the command is simply
**not registered** — it is invisible to `?`/help and tab-completion, and invoking
it yields `unknown command` (exit `127`). The decorated function is still returned
unchanged, so it remains a normal Python callable.

Because one shell process serves exactly one identity, the profile (and therefore
the registered command set) is fixed for the life of the process; the policy is
read and cached once.

## Assigning a profile

`users add <email> [profile]` seeds the invite with the chosen profile
(`admin` / `user` / `guest`; default `user`), stored on the invited account and
preserved through registration and password resets. Example:

```
users add alice@example.com          # a standard user
users add bob@example.com guest      # read-only browse access
users add carol@example.com admin    # full access
```

The per-command availability (both channel and profile) is listed in
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
provider's pair), `SMTP_ADDRESS`, `SMTP_APP_PASSWORD`, optional `EULER_BASE_URL`.
Every auth file is now a dot-file, so `**/.*` in `.gitignore` covers all of them
(`.users.json`, `.pending.json`, `.remember.json`, `.session-secret`,
`.server.crt`, `.server.key`) — no per-file `.gitignore` entries needed.

| Layer | Setting |
|---|---|
| DNS provider | API token; `_acme-challenge` TXT via acme.sh; the `euler` A record via the DDNS updater (public only) |
| acme.sh | issues/renews via the provider's DNS-01 hook; deploys cert to `keys/`; reloads Caddy |
| Caddy | stock apt build; loads `keys/.server.crt` + `keys/.server.key`; runs as the repo owner |
| aiohttp | `solver-web`, bound to `127.0.0.1:8080`; SRP auth gate in `solver/web/auth/` |
| Router | forward TCP 443 → the host's LAN IP; static lease (public only) |
| System firewall | inbound allow TCP 443 (public only) |

## Verify

1. `scripts/setup/caddy.sh status` shows Caddy installed and the default service
   inactive/disabled.
2. `keys/.server.crt` and `keys/.server.key` exist (key mode `0600`);
   `caddy validate --config Caddyfile` passes and the service logs the loaded
   certificate (no ACME attempt).
3. `solver "users add you@example.com"` emails a 24 h secure link (or prints it if
   SMTP is unconfigured); opening it loads `/register?token=…`, and setting a policy-
   compliant password completes registration. Then log in at `/login` — the password
   never appears in a request body (browser-side SRP). A tampered or expired token
   shows an error and no form; `/register` with no token is not linked anywhere.
4. From a LAN device: `curl -v https://euler.vikasmunshi.com/login` returns the
   login page over a valid, browser-trusted certificate; an unauthenticated
   `curl` of a gated page redirects to `/login`.
5. After login, the `/ws` shell connects; an unauthenticated WebSocket upgrade is
   rejected before a socket is handed out.
6. To go public: add the router forward + firewall rule, wire DDNS, and re-test
   from outside the LAN.

## Renewal & operation

- **acme.sh** renews the certificate (cron re-issues before expiry) and runs
  `--reloadcmd` to reload Caddy — no Caddy-side ACME involved.
- Run the dedicated **`caddy-euler.service`**, not the packaged default; it runs as
  your user so it can read `keys/`. Do not re-enable the default `caddy.service`.
- **DDNS** (public only) runs from its own timer/cron.

## Sources

- [acme.sh](https://github.com/acmesh-official/acme.sh) ·
  [dnsapi guide](https://github.com/acmesh-official/acme.sh/wiki/dnsapi)
- [Caddy `tls` directive (manual certificates)](https://caddyserver.com/docs/caddyfile/directives/tls)
- [Accessing network applications with WSL — Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [Hyper-V Firewall — Microsoft Learn](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/hyper-v-firewall)
- [RFC 5054 — SRP for TLS](https://datatracker.ietf.org/doc/html/rfc5054)