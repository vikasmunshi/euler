# Web server guide

The self-hosted `solver` web front end: a TLS edge, an SRP authentication service, and
one per-collaborator application instance, wired together over unix sockets behind a
kernel egress firewall.

Its purpose shapes every decision in it. The front end exists to give an invited
collaborator a real `solver` shell in a browser — **remote code execution is the
product, not an accident**. Nothing here pretends the shell is not a shell. The design
spends its effort instead on two things: making identity **unforgeable**, and making a
compromise's blast radius **one collaborator's own sandbox**.

The organising principle is **one uid per collaborator**. Each has their own system
user, home, repo clone, git branch, and encrypted vault of secrets. A secret that rests
on a user's uid is exposed only to that user's own code, which is not a leak — they own
it. Kernel identity replaces claim-passing between services, and git works natively
because each user pushes as themselves.

- [1 · Shape](#1--shape)
- [2 · The edge](#2--the-edge)
- [3 · Egress](#3--egress)
- [4 · Authentication](#4--authentication)
- [5 · Identity](#5--identity)
- [6 · Authorization](#6--authorization)
- [7 · The per-user tier](#7--the-per-user-tier)
- [8 · The vault](#8--the-vault)
- [9 · Private solutions: the enc-key layer](#9--private-solutions-the-enc-key-layer)
- [10 · Git](#10--git)
- [11 · The site](#11--the-site)
- [12 · The web shell](#12--the-web-shell)
- [13 · Security posture](#13--security-posture)
- [14 · Operating it](#14--operating-it)

## 1 · Shape

```
                         :443
 browser ───TLS──▶  ┌───────────┐  edge: TLS, security headers
                    │   Caddy    │  · strips client X-User / X-Profile / X-User-Slug
                    │  (edge)    │  · forward_auth ──────────────┐
                    └─────┬──────┘  · routes by X-User-Slug      ▼
           unix sockets /run/euler                        ┌─────────────┐
                          │                               │    auth      │ SRP login,
                          │                               │   service    │ sessions,
                          ▼                               │  (aiohttp)   │ invites,
        ┌──────────────────────────────────┐              └──────┬──────┘ shell tickets
        │  euler-user@<slug>               │◀────────────────────┘
        │  User=euler-user-<slug>          │   200 + X-User + X-Profile + X-User-Slug
        │  serves this collaborator's      │   or 401 → /login
        │  content routes AND /ws          │
        │                                  │       ┌─────────┐  allowlist egress only
        │  ~/euler   their clone, branch   │──────▶│  Squid   │─▶ api.anthropic.com,
        │            user/<slug>           │       │ (egress) │   projecteuler.net,
        │  ~/.euler  their vault (0700)    │       └─────────┘   github, claude.com
        └──────────────────────────────────┘
                          ▲
        policy: /etc/euler/authorizations.json — read by the shell and every service
```

Only Caddy is network-bound. Every application service listens on a unix domain socket
under `/run/euler/`, which makes filesystem permissions the access control: the socket
is `0660 euler-<svc>:euler-web`, so only group members can `connect()`. There is no port
registry to maintain and no `0.0.0.0` mis-bind one typo away. Isolation is only real
across distinct uids, so each service gets a dedicated nologin system user, and **none
runs as root**.

| Service | User | Socket / port | Role |
|---|---|---|---|
| edge | `euler-caddy` | `:443` (public) | TLS, header stripping, `forward_auth`, routing |
| auth | `euler-auth` | `/run/euler/auth.sock` | SRP login, sessions, invites, shell tickets |
| per-user app | `euler-user-<slug>` | `/run/euler/user-<slug>.sock` | one collaborator's content routes + `/ws` |
| admin plane | `euler-auth` | `/run/euler-adm/auth-admin.sock` (`0600`) | account mutations; never routed by Caddy |
| egress proxy | `euler-proxy` | `127.0.0.1:3128` | Squid domain allowlist |
| mail relay | `euler-smtp` | `127.0.0.1:8025` | sole holder of the Gmail credentials |
| certificates | `euler-acme` | — | acme.sh DNS-01, on a daily timer |
| dynamic DNS | `euler-ddns` | — | keeps the A record on the current public IP |

Application **code** runs from a root-owned system venv at **`/opt/euler`**, never the
repo checkout — the service users cannot traverse the repo owner's `0750` home, and
keeping code out of a writable tree means a repo write cannot change what executes. The
framework is aiohttp + Jinja2 with autoescape on.

Pages are composed **server-side** and updated by swapping rendered HTML fragments
(htmx). There is no SPA, no client-side router, no JSON-assembly in the browser, and no
build toolchain. This is not asceticism: it means all escaping is Jinja's, server-side,
so the DOM-XSS class does not exist here, and one template renders both a full page and
the fragment that updates it.

## 2 · The edge

Caddy terminates TLS on `:443` as the unprivileged `euler-caddy`
(`AmbientCapabilities=CAP_NET_BIND_SERVICE` rather than root), loading a certificate by
absolute path from `/etc/euler/tls/`. It performs no ACME of its own.

**Certificates come from acme.sh over DNS-01**, run as `euler-acme` on a daily timer.
DNS-01 needs no inbound port, so nothing listens on `:80`. Caddy's own ACME is not used
because the `caddy-dns/namedotcom` plugin is unmaintained and no longer builds against
current Caddy; delegating issuance to acme.sh keeps the DNS-01 benefit with stock Caddy.
Renewal re-applies the key mode and reloads through **Caddy's admin API** on loopback
`:2019` rather than `systemctl`, so the non-root `euler-acme` can trigger it. The cert
directory is `euler-acme:euler-web` setgid `2750`, so acme.sh's writes inherit the group
and `euler-caddy` reads the key at `0640` — no chown, no root.

The same name.com token drives DNS-01 and the `euler-ddns` timer, which PUTs the A
record only when the public IP changes.

The generated `/etc/euler/Caddyfile` (`0644`, non-secret) does four things:

1. **Strips `X-User`, `X-Profile`, and `X-User-Slug`** from every inbound request,
   before any routing. These are identity, and identity may only ever reach the app tier
   as a copy of the `forward_auth` response.
2. Serves `/healthz` natively and `/assets/*` + `/vendor/*` statically from
   `/etc/euler/web-content`, so pages reference `'self'` assets and the CSP holds.
3. Proxies the **public auth surface** — `/login`, `/register*`, `/reset*`, `/forgot`,
   `/password`, `/terms`, `/auth/*` — straight to `auth.sock`. The shell-ticket and
   admin endpoints are deliberately absent from this list; they are socket-peer only.
4. Gates **everything else** through `forward_auth` to `/auth/check`, then routes the
   request to its user's own socket:

```
@user header_regexp X-User-Slug ^[a-z][a-z0-9-]{1,30}$
reverse_proxy unix//run/euler/user-{http.request.header.X-User-Slug}.sock
```

A request-header placeholder in the dial address is enough — no dynamic-upstream module.
The `header_regexp` matcher admits only a well-formed system slug; anything missing or
malformed falls through to the 503 holding page, which is also what a deprovisioned
user's dead socket produces via `handle_errors`. The WebSocket upgrade survives the
placeholder upstream, so content and `/ws` share the one route.

Caddy adds the transport headers that need no per-response state — HSTS,
`X-Content-Type-Options`, `Referrer-Policy` — plus a **fallback** CSP using the
set-if-absent (`?`) operator, so it applies only to Caddy-native responses that carry no
application CSP of their own.

## 3 · Egress

"Egress only via Squid" is enforced at the **kernel**, not by an environment variable a
compromised process can simply ignore. Two layers.

**Squid** runs on loopback `127.0.0.1:3128` as `euler-proxy` with a default-deny domain
allowlist (`api.anthropic.com`, `.projecteuler.net`, `.github.com`,
`.githubusercontent.com`, `.claude.ai`, `.claude.com`, `.anthropic.com`). Client-side
`HTTPS_PROXY`/`HTTP_PROXY` is written to `/etc/euler/egress.env` and loaded by the
service units, so AI features, the problem scraper, and `gh` egress only through it. The
allowlist lives in `/etc/euler-proxy/squid.allowlist` — edit and reload.

**nftables** (`scripts/setup/firewall.sh` → `euler-firewall.service`) makes that
structural. A `table inet euler` with an egress-only (`hook output`) chain permits
loopback and only the specific `(uid, port)` each service needs, then drops the rest:

| uid | Permitted egress |
|---|---|
| `euler-proxy` | `tcp dport {80,443}` — the **only** service with real internet |
| `euler-acme` | `tcp dport 443` (ACME + DNS provider) |
| `euler-ddns` | `tcp dport 443` (name.com, ipify) |
| `euler-smtp` | `tcp dport 587` (Gmail submission) |
| infra uids | `udp/tcp dport 53` |
| every `euler-*` | loopback; **everything else dropped** |

Two details matter and are easy to get wrong:

- The chain is **`policy accept`** and drops only the enumerated `euler-*` uids via a
  final `skuid { … } drop`. SSH, root, and your own shell are untouched — there is no
  lock-out risk.
- **Loopback is matched by destination address** (`ip daddr 127.0.0.0/8` / `ip6 daddr
  ::1`), never by `oif "lo"`. The interface-index match does not hit loopback output on
  the WSL2 kernel: euler uids' loopback SYNs fell through to the final drop while replies
  still passed on `ct state established`, so only *new* service-to-service connections
  broke. The address space is also the actual security intent.

Per-user uids are created dynamically at provision time, so the generator enumerates
them **by prefix** (`euler-user-*`) and folds them into the drop. Because the chain is
policy-accept, an un-enumerated uid would reach the internet directly, bypassing Squid —
which is why `provision` reloads the firewall.

**Mail** is the founding case of the principle that a secret lives only with the service
that performs its operation. Rather than granting the app tier a direct-internet
exception for SMTP, `euler-smtp` listens on loopback `:8025`, is the **sole holder of
the Gmail credentials** and the **sole uid permitted `:587`**, forces the envelope
sender, and never logs bodies (they carry one-time codes). A firewall relay guard bars
every other `euler-*` uid from `:8025` — including a hostile web shell. `euler-auth`
submits mail over loopback holding no credentials at all.

## 4 · Authentication

Login is **browser-side SRP-6a**: the password never crosses the wire and never reaches
the server or its disk. The server stores only `{salt, verifier}`; each side proves
knowledge through a challenge/response, and the client verifies the server back.

This is not merely good hygiene here — it is load-bearing for [the vault](#8--the-vault).
Because the server never sees the password, it cannot derive the key that unwraps a
user's secrets, which is exactly what makes those secrets opaque to the operator at rest.

### 4.1 Registration and reset

Registration is **invite-only and two-channel**: an admin mints an invite, and the
invitee proves *live* mailbox control before any password is set. Every secret is stored
hashed, and every step is single-use and time-boxed. State lives in
`/var/lib/euler-auth/pending.json`, keyed by `hash(link-token)`, walking `invited →
otp_sent → verified → (consumed)`:

1. **Invite** — `users add <email> [profile]` provisions the account (§7) and mints a
   pending record, emailing `https://<FQDN>/register?token=<32-byte token>`. No user
   record exists yet.
2. **Open link** — a valid, unexpired `invited` token renders the page: the email
   read-only, the Terms in a scroll box whose accept checkbox unlocks only at the end of
   the text, and "email me a code". Anything else renders a generic "link not valid"
   page.
3. **Accept Terms, request OTP** — records the acceptance, mints a 6-digit OTP
   (`hash(otp)`, +10 min, `attempts=0`), and emails it. Resends are capped.
4. **Verify OTP** — a match under 5 attempts moves to `verified`; **5 failures
   invalidate the OTP** and a fresh one must be requested.
5. **Set password** — the browser derives `{salt, verifier}` locally from a
   policy-compliant password and posts them with the account's display name. This
   creates the `users.json` entry, consumes the pending record, and lands on `/login`
   (no auto-login).

The two secrets do different jobs: the **link token** (32 bytes, 7 days) proves
possession of the invite; the **OTP** (6 digits, 10 minutes, 5 tries) proves live
mailbox control *at completion time*. Both are stored only as hashes and never logged.

**Reset is self-service** — admins never reset passwords. `/forgot` runs the identical
link → OTP → set-password pipeline with Terms skipped, and its responses are **generic
regardless of whether the email exists**. Completing a reset revokes every live session
and remember-me token — and destroys the vault, deliberately (§8.2).

### 4.2 The login handshake

1. `POST /auth/challenge {email}` → the service loads `{salt, v}`, computes `B = k·v +
   gᵇ`, and replies `{salt, B}`. **Unknown or disabled accounts get a stable decoy**
   `salt`/`B` (never stored), so the response reveals nothing.
2. `POST /auth/verify {email, A, M1, remember}` → the server checks `M1`; on success it
   replies `{M2, email, profile}` and sets the session cookie (plus the remember-me
   cookie if asked). On failure, a generic 401.
3. The browser verifies `M2` — mutual authentication — and is logged in.

The browser client (`solver/web/content/assets/srp.js`) interoperates byte-for-byte with
`srp.py`: RFC 5054 2048-bit group, `g=2`, SHA-256, `PAD`-to-`|N|` on `A`/`B`/`S`.
`tests/test_srp_interop.py` cross-tests them (needs `make install-nodejs`).

### 4.3 Sessions and remember-me

- **Session** `solver_session`: an opaque token → in-memory `(email, profile, expiry)`,
  12 h TTL, `Secure; HttpOnly; SameSite=Lax; Path=/`. Sessions are per-process; a
  service restart drops them all.
- **Remember-me** `solver_remember`, only when requested: a selector\:validator token
  whose server side (`selector → (email, HMAC(validator), expiry)`) lives in
  `remember.json` and survives restarts, 30-day TTL. With a valid remember cookie and no
  session, `POST /auth/resume` verifies it in constant time, **rotates the validator**
  (one-time use), and opens a fresh session. A wrong validator revokes the selector —
  that is theft detection, not just hygiene. Logout clears both cookies and deletes the
  server-side record.

### 4.4 The `forward_auth` endpoint

`GET /auth/check` is what Caddy calls on every gated request: a live session returns
`200` with `X-User` (email), `X-Profile`, and `X-User-Slug`; no session returns `401`,
which Caddy turns into a `302 /login` for browser navigations. Caddy copies those
headers onto the proxied request **after deleting any client-supplied copies**, and the
app sockets are unreachable except through Caddy — which is why downstream services can
trust them.

### 4.5 Policy constants

`solver/web/auth/policy.py`:

| Constant | Value | Meaning |
|---|---|---|
| `SESSION_TTL_SECONDS` | 12 h | session lifetime (in-memory) |
| `REMEMBER_TTL_SECONDS` | 30 d | remember-me lifetime (rotated on use) |
| `CHALLENGE_TTL_SECONDS` | 120 s | pending SRP challenge hold |
| `MIN_PASSWORD_LENGTH` / classes | 16 / lower+upper+digit+special | password policy (client-enforced) |
| `INVITE_TTL_SECONDS` / `LINK_TOKEN_BYTES` | 7 d / 32 | emailed link validity / entropy |
| `OTP_DIGITS` / `OTP_TTL_SECONDS` / `OTP_MAX_ATTEMPTS` / `OTP_MAX_SENDS` | 6 / 10 min / 5 / 5 | one-time code |
| `TICKET_TTL_SECONDS` | 60 s | one-time shell ticket |
| `AUTH_RATE_MAX` / `AUTH_RATE_WINDOW_SECONDS` | 30 / 60 s | per-client rate limit on unauthenticated endpoints |
| `PROFILES` | `reader`, `contributor`, `maintainer` | web-assignable profiles for the admin API |

### 4.6 State

`/var/lib/euler-auth`, `euler-auth`-only `0600`, shared with no other uid — not even the
repo owner. The admin commands never touch these files; they call the service (§6.3).

| File | Purpose |
|---|---|
| `users.json` | SRP verifier DB: `{salt, verifier, name, terms_version, terms_accepted_at, created, disabled}` per email. `name` is the display name, used for git authorship. **No profile** — that lives in `authorizations.json`, resolved fresh at each login. |
| `pending.json` | in-flight invites and resets, keyed by `hash(link-token)`. |
| `remember.json` | remember-me `selector → (email, HMAC(validator), expiry)`, rotated on use. |
| `session-secret` | 32-byte HMAC key for remember-me; created on first start. |

## 5 · Identity

`solver/auth` resolves a single **subject** once per process, at startup, with no
anonymous fallback:

```
Subject(user, slug, channel, auth_method, profile)
```

`user` is the raw identity (email on the web, OS login in a terminal); `slug` is its
filesystem-safe form; `channel` is `terminal` or `web`; `auth_method` records how
identity was proven, for audit. Nothing else in the codebase re-derives identity.

Three planes, each with an explicit voucher, tried in order:

| Plane | Voucher | Mechanism |
|---|---|---|
| Web shell | auth service | `SOLVER_TICKET` — a one-time ticket redeemed over `auth.sock` |
| Per-user instance | the OS | a `euler-user-<slug>` uid whose `EULER_USER_SLUG` pin maps back to its own handed-down email |
| Local terminal | the OS | `os.getuid()` owns the repo checkout → `admin`; a real non-owner login → `contributor` |

**The shell ticket.** Nothing carried in the environment can be a credential:
`/proc/<pid>/environ` is same-uid-readable, so anything there is readable by any sibling
process of that user. Instead, on WebSocket attach the service forwards the caller's
session cookie to `POST /shell-ticket`, which mints a **single-use, 60-second** ticket
bound to `(email, profile, display name)`; the forked child redeems it at startup, which
consumes it and returns the authoritative identity. Missing, expired, or reused → the
shell aborts. Minting requires a live session cookie the shell user does not hold, and
the `/shell-ticket*` endpoints are not routed by Caddy.

**The slug pin.** A redeemed ticket whose `system_slug(email)` differs from the forking
instance's `EULER_USER_SLUG` **aborts**. That instance *is* that user's uid — with their
home, keys, and clone — so a ticket for anyone else means misrouting or a bypass, and
the process must not run.

**Service uids.** A `euler-*` uid that is neither a ticketed web shell nor a properly
pinned per-user instance **aborts**. This is what stops a web shell from running `unset
SOLVER_TICKET; solver` to re-resolve itself into a different identity. There is no
assume-an-identity path: `SOLVER_USER` is display-only.

**The local terminal.** The profile is the `authorizations.json` `users`-map value for
the OS login. The **checkout owner floors to `admin`** when unlisted — you cannot lock
yourself out of your own checkout — but an explicit entry wins, so the operator can
deliberately run local at a lower rung. Anyone else with an entry-less real login gets
`contributor`.

The slug scheme is worth one note. `slugify` emits a `.`-bearing form
(`mercanther_gmail.com-3f9e97`) that **fails `useradd`'s `NAME_REGEX`**, so the system
slug used for uids, homes, sockets, and `X-User-Slug` is a stricter derivation:
`[a-z][a-z0-9-]*`, a sanitized and truncated local-part plus a short hash suffix,
bounded so `euler-user-<slug>` stays well under the name limit (e.g.
`euler-user-vikas-munshi-0a68e0`, 30 chars). The email remains the login identity; the
slug is the derived system identity.

## 6 · Authorization

Authorization is a **plain profile ladder**. A command or route declares the *minimum
profile* it needs, and enforcement is a rank comparison:

```
reader  <  contributor  <  maintainer  <  admin
```

The ladder is **structural, not configuration** — code, templates, and the provisioning
kits all branch on these names — so it lives in code (`solver/auth/subject.py::LADDER`).
`authorizations.json`'s optional `ladder` field documents it and is validated on load; a
mismatch fails loudly rather than silently reordering trust.

Declaring that floor is **mandatory** — `requires` is a required
`Literal['reader', 'contributor', 'maintainer', 'admin']` on the decorator, so a command
that omits it is a type error rather than a silently-exposed command. There is no default
to get wrong.

### 6.1 The policy file

`/etc/euler/authorizations.json` (`root:root 0644`) is the system of record, and it
carries exactly one decision — **who has which profile**:

```json
{
  "ladder": ["reader", "contributor", "maintainer", "admin"],
  "users": {
    "vikas": "admin",
    "vikas.munshi@gmail.com": "maintainer"
  }
}
```

The `users` map is keyed by **web email or OS-login name**, one map for both channels.
It is world-readable because it is not secret, and **root-write only** because every
mutation goes through the sudo-gated `users` path. It lives outside the repo so that a
repo write cannot change policy. There is **no policy file in the repo**: absent a
deployed one the built-in default maps nobody, so the checkout owner floors to `admin`
by uid and everyone else is `contributor`. The installer seeds the real file.

This file used to carry `profiles`/`grants`/`objects` — an `object:permission` grant
vocabulary whose real job was deriving per-path filesystem ACLs on a *shared* operator
tree. Per-user uids retired that entire layer: each collaborator is alone in their own
clone, so there is nothing to partition by path. A legacy-shaped file still loads; only
its `users` map is read.

### 6.2 Enforcement

- **Shell, at decoration time.** As each command module imports, `@register` checks the
  declared floor against the subject's profile. If it does not clear, the command is
  **not registered** — invisible to `?`, help, and completion, and `unknown command`
  (exit 127) if invoked. One process serves one identity, so the set is fixed for the
  process's life.
- **Web routes.** The app router gates each route against the requester's `X-Profile` —
  the same policy, the same ladder.

`modules.csv` is a **pure loader manifest** (`module, registers_commands`). Every module
imports; commands the subject cannot hold simply do not register.

The channel (terminal vs web) is **not** an authorization axis. In the per-user model
the isolation boundary is the uid, and a user's web shell is a shell in *their own*
sandbox — no different from their terminal — so gating on channel earned nothing.
`subject.channel` survives informationally: `show`/`edit` still branch browser-tab
versus OSC-to-pane.

Dropping that axis had one consequence worth stating, because it removed a backstop
rather than a redundancy: **`users list` had been kept off the web by the channel gate
alone**, and its non-admin path printed the whole roster — every collaborator's email
and profile. The fix belongs at the command, not the ladder: `users list` for a
non-admin is scoped to the caller's **own entry**, and the full roster is an admin view.

**Staleness is re-login.** The subject resolves once at process start, so a policy edit
takes effect at the next login or shell start. `users change`/`disable`/`remove` and
password reset all revoke sessions, and the auth service additionally pushes a teardown
to any live web shell (§12) — so revocation is immediate on every plane, not deferred
until a running process happens to die.

### 6.3 Administration — the `users` command

`users` splits by verb. **`users list`** registers at the `reader` floor and
self-scopes for non-admins. The **mutating verbs require `admin`** and go through the
**wheel-gated admin plane**: the CLI (`solver.web.auth.admin`) re-executed under `sudo`,
writing the root-owned policy file and reaching the euler-auth admin socket.

Sudo rather than a bespoke admin group is deliberate. The operator is a sudoer anyway,
and the operator's *ordinary* uid is the most exposed on the host — browsers, dev
tooling, AI agents all run there. An operator-readable admin token would let any of them
silently mint admin invites, gating the highest-privilege API *below* sudo. The token
lives only in root-readable `auth.env`, and the admin socket (`0600`, euler-auth-private)
is never routed by Caddy.

```bash
users list                                    # roster; non-admins see only their own entry
users add alice@example.com                   # WEB: provision + mint an emailed invite (default: reader)
users add bob@example.com contributor         # WEB: invite a contributor
users add vikas admin                         # LOCAL: a bare os-login → direct map entry, no invite
users change alice@example.com contributor    # promote / demote
users disable alice@example.com               # also kills live sessions + remember tokens
users enable  alice@example.com
users remove  alice@example.com               # delete the account/entry, pending invites, and deprovision
```

**`add` has two paths.** An `@`-address is the **web** path: provision the collaborator
(§7), write the map entry, and mint an emailed invite — provisioning happens *before* the
invite, so there is never a dangling invite to a box with no shell. A bare **os-login**
is the **local** path: just the map entry, no invite, because a local login authenticates
by *being* that OS user.

**`admin` is assignable only to a local os-login.** The admin API validates a web
identity against `reader`/`contributor`/`maintainer`. The identity resolver, by
contrast, does *not* cap a redeemed ticket — so an email mapped to `admin` out-of-band
(a root edit of the policy file) would carry admin over the web. That is the accepted
posture in §13, not an oversight: containment for the highest-privilege operations is the
profile grant plus SRP plus uid isolation, with no channel backstop.

There is no reset verb — reset is self-service.

### 6.4 Command floors

Every command's declared floor is generated from the live registry into
[`authorizations.md`](authorizations.md) by `update-docs`. The shape of it:

| Floor | Commands |
|---|---|
| `reader` | `ls`, `show`, `results`, `test-cases`, `problems`, `progress`, `search`, `git-status`, `git-sync`, `git-filter`, `user`, `vault`, `users` (self-scoped list), `?`/`echo`/`clear`/`pause`, `key-reconstruct` |
| `contributor` | `new`, `edit`, `evaluate`, `benchmark`, `compile-c`, `lint`, `mark`, `!`, `claude-api`, `claude-solve`, `costs`, `git-commit`, `git-push`, `git-hooks`, `git-identity` |
| `maintainer` | `summary` (rewrites the shared progress state), web file-delete |
| `admin` | `users` mutations, `user-authorize`, `key-rekey`, `key-split`, `git-merge`, `git-publish`, `manage-config`, `update-docs`, `update-models`, `pip-upgrade`, `sys-setup` |

Two floors deserve their reasoning. **`!` (raw bash) sits at `contributor`**, not admin:
in the per-user model a shell escape grants nothing that `evaluate`'s arbitrary Python
did not already, and it is the user's own uid sandbox either way. **AI commands sit at
`contributor`** because the credentials are the user's *own* Anthropic key from their own
vault — it is their spend, not the operator's.

## 7 · The per-user tier

One systemd template instance per collaborator — `euler-user@<slug>.service`,
`User=euler-user-<slug>` — serves **both** that user's content routes and their `/ws`
shell, all operating on their own `~/euler`. Caddy routes every request for a user to
their one socket by `X-User-Slug`.

Each instance is **born as the right uid**: no process changes uid, nothing runs as
root, no setuid anywhere. It is **socket-activated** (`euler-user@<slug>.socket`), so
idle invitees cost nothing and systemd starts the instance on first attach.

Content and shell are one service because the isolation boundary is now the uid. Splitting
them would separate two things that already share a sandbox — one service kind, one
socket per user.

```
home  /home/euler-user-<slug>/                     (0700, uid-private)
  ├─ euler/          their repo clone — content, branch user/<slug>
  │    └─ solutions/private/**   ciphertext until enc-key authorized (§9)
  └─ .euler/         their vault (§8)
       ├─ id         their X25519 private key, encrypted under the vault key
       ├─ env        their ANTHROPIC_API_KEY etc., encrypted
       ├─ vault      {salt, iterations, wrapped_vk}
       └─ user_pass  (terminal path only) the password, to derive the key off-line
```

**The application is shared and read-only; the content is per-user.** One `/opt/euler`
venv everyone runs, pointed at each user's own tree with `EULER_REPO_ROOT=~/euler`.

The `~/euler` + `~/.euler` layout is not cosmetic: `solver.config` already derives the
secrets directory as `root_dir.parent/.{root_dir.name}`, so a repo root of `~/euler`
yields a secrets dir of `~/.euler` with **no new path logic** — the private key, env
file, and `.state` all fall into place per-user for free.

**Defence in depth on routing.** The instance carries an identity middleware that refuses
any request whose `X-User` maps to a different `system_slug`. In production Caddy already
routes by the slug `forward_auth` returned, so this only ever agrees — it is the code-side
backstop if the edge is ever misconfigured.

### 7.1 Provisioning

Account creation is an admin act, from a terminal, under sudo, and **it handles no
secrets at all**. `users add <email> <profile>` drives `scripts/setup/user.sh`:

1. create the system user `euler-user-<slug>` and its `0700` home;
2. clone `~/euler` **directly from the public GitHub repo** — anonymous read, no
   credentials — with the crypt filter **disabled**, checked out on a fresh branch
   `user/<slug>`. Origin stays the GitHub URL, so the user pushes as themselves later;
3. lay down `~/.euler` (`0700`) and the socket-activated instance;
4. mint the web invite; the user sets their password, and their vault initialises on
   first login;
5. no keys, no Anthropic secret — those are the user's own later, self-service steps.

**The clone lands ciphertext for free.** The crypt filter is registered in a clone's
*local* git config, which is never cloned, plus a *tracked* `.gitattributes` rule. A
fresh clone inherits the attribute but not the filter definition, so encrypted blobs pass
through untouched. GitHub only ever holds the filter's ciphertext anyway. So a user who
is not yet key-authorized cannot read private plaintext even though the files sit in
their own home — the git filter enforces the enc-key layer with no extra machinery.

**Teardown** (`users disable` / `remove`) stops and disables the instance and removes the
home. Dropping the account's master-key access is a **separate admin act** (`key-rekey`,
§9) — it needs the master key, which the root provisioning plane deliberately never
touches.

## 8 · The vault

A user's secrets — `~/.euler/id` (their X25519 private key) and `~/.euler/env` (their
Anthropic key and anything else) — are stored **encrypted**, so they are opaque to the
operator at rest rather than protected by file permissions alone.

**Envelope encryption**, not direct password encryption:

- A random per-user **vault key `VK`** (32 bytes) encrypts the secrets with AES-256-GCM,
  a fresh nonce per blob. A magic header marks a file as vault ciphertext, so plaintext
  and encrypted forms both load transparently.
- `VK` is stored **wrapped** under `PK = PBKDF2-HMAC-SHA256(password, salt, 600 000)`,
  reusing the SRP salt, in `~/.euler/vault` — which also records the salt and iteration
  count, so the terminal path is self-contained.
- Use: derive `PK` → unwrap `VK` → decrypt. A password change **re-wraps only the small
  `VK` blob**; the secrets are never re-encrypted.

PBKDF2 rather than scrypt because it is **WebCrypto-native**: the browser derives the
identical `PK` from the password it already holds and the salt already in the SRP
challenge — no bundled KDF, no extra round-trip. 600 000 rounds is the OWASP floor for
PBKDF2-SHA256. The cost is paid once per session.

### 8.1 Delivering the key

The code that needs `VK` — `load_private_key` and the git clean/smudge filter — runs in
**subprocesses** (git spawns the filter once per file), so `VK` must reach the user's
children, not just their interactive shell.

`VK` lives in a **uid-private tmpfs file** (`0600`), written at session start and removed
at session end. Only its **path** is exported, as `EULER_VAULT_KEY_FILE`, and inherited
by subprocesses so the filter finds it. The key itself is never in any process's
environment — not in `ps e`, not in core dumps, not in every child's `/proc/environ` —
only in the tmpfs file and, transiently, in the memory of the code decrypting with it.

Where `VK` comes from:

- **Web** — the browser derives `PK` at login and passes it to the user's own service at
  shell attach; the service unwraps `VK` and writes the tmpfs file. `PK` and `VK` never
  touch server disk. The terminal page unlocks *before* the first `/ws` attach, so the
  forked shell inherits the key file. Note that the auth service **cannot** derive `PK` —
  it never sees the password — which is precisely what keeps the vault opaque.
- **Terminal** — `~/.euler/user_pass` (uid-private) holds the password and the shell
  derives `PK` at start. Weaker, and knowingly so: it is the terminal-convenience path,
  and that user is typically the operator on their own box.

The routes are on the user's own service: `GET /vault/status`, `POST /vault/unlock`
(unlock, or initialise on first login with the SRP salt; a mismatched `PK` returns 409
`stale`, never destructive), `POST /vault/rewrap`, and the socket-peer
`POST /internal/vault-reset`. The browser keeps `PK` in `sessionStorage` and auto-unlocks
on page load. Logout locks the vault and removes the key file.

### 8.2 Change versus reset

These differ fundamentally, and the difference is a feature.

- **Change (current password known): the vault survives.** `PK` is derivable from the old
  password, so `VK` is simply re-wrapped under the new one. Cheap and lossless.
- **Reset (password forgotten): the vault does not survive — by design.** `VK` is
  recoverable *only* from the password. An SRP reset re-mints the login verifier and
  shares nothing with the vault, so the new password's `PK` cannot unwrap the old `VK`.
  The secrets are unrecoverable and must be re-provisioned: `user --regen` (new keypair →
  admin re-authorizes) plus re-uploading the Anthropic key. The reset flow re-initialises
  the vault rather than leaving a stale blob wrapped under a dead `PK`.

That destruction is the point: **a malicious operator cannot use reset as a covert vault
backdoor**, because a reset visibly destroys the vault — the user's keys stop working. A
recovery-code escape hatch is deliberately not offered; it would add a second `VK` holder
and weaken exactly this property.

### 8.3 What the vault does and does not promise

State it precisely, because the honest boundary is narrower than "zero-knowledge" and
over-claiming here would be worse than not having the feature.

The secrets are **used server-side** — the Anthropic key by `claude-api`, the private key
by the git filter, both in the user's own shell process — so at time of use `VK` and the
plaintext are in server memory. **A malicious active root can read that memory (ptrace)
or modify the shared solver code to exfiltrate.** No design protects a secret from the
entity that controls the CPU it runs on.

The guarantee is therefore exactly: **encrypted at rest and opaque to a passive or honest
operator; not protected against a malicious active root.** This is the same boundary the
master key has always lived with — root could always scrape it from a smudging process —
so the vault extends at-rest opacity to per-user secrets rather than claiming something new.

### 8.4 The `vault` command

`vault status | init | change-password`. `init` migrates the operator's own plaintext
`~/.euler/id` and `env` in place. `user --regen` persists the new key vault-encrypted
when a vault is unlocked, and refuses when locked.

## 9 · Private solutions: the enc-key layer

Trust is **two independent dials**, and every combination is valid:

| Layer | Grants | Mechanism | Set by |
|---|---|---|---|
| **Ladder** | which *commands* you may run | `authorizations.json` | admin, at `users add` / `users change` |
| **enc-key** | whether you can see **private-solution plaintext** | your X25519 public key wrapped into `keys/enc-key.json` | admin, later, on request |

A `contributor` without a key edits public problems and sees **ciphertext** for private
ones; a `contributor` with a key can decrypt and edit them; a `reader` with a key can
read private plaintext but not edit. The ladder is a **capability** gate; enc-key is a
**content-visibility** gate. They do not interact.

The crypto master key is wrapped, per authorized public key, in the tracked file
`keys/enc-key.json` — proof of possession: hold the matching private key, unwrap the
master key, smudge and clean. (See [gitfilter-guide.md](gitfilter-guide.md).)

- **Each user has their own X25519 keypair.** The private key lives in their vault; the
  public key is enrolled by an admin.
- **Authorization is a deliberate admin trust act**, never self-service — it grants
  decryption of the *whole* private corpus. The flow: the user generates their key in
  their shell (`user`), reads the public key off their account page, and passes it to an
  admin **out of band**; the admin runs `user-authorize <pubkey>` and commits and pushes
  `keys/enc-key.json`; the user pulls, and their key now unwraps the master key. **The
  distribution channel is git itself** — no side channel.
- **Revocation** is `key-rekey` (rotate the master key, re-wrap only to still-authorized
  keys) plus a push. The de-authorized user's next pull decrypts nothing.

`user-authorize` and `key-rekey` never need a *user's* private key, so the vault never
interferes with enrollment or rotation. A user can have a working vault and no master-key
access at all — their pubkey simply is not in `enc-key.json`.

## 10 · Git

Git is **native** in the user's own clone — there is no broker, and nothing proxies it.
`git-status`/`git-sync` sit at `reader`; `git-commit`/`git-push`/`git-hooks`/`git-identity`
at `contributor`; `git-merge`/`git-publish` at `admin`.

- **`git-identity`** (`scripts/git/configure-identity.sh`) is the user's one-time
  self-service setup: `gh auth login` (device flow, which works in a web shell), `gh auth
  setup-git`, and `user.name`/`user.email` from their GitHub profile. Their commits are
  authored and pushed as **them**.
- **`git-sync` carries the enc-key pull flow.** After the pull, if the filter is unwired
  and `read_master_key()` now verifies — meaning an admin authorized this user's key and
  pushed — it wires the clean/smudge filter and re-checks out `solutions/private`.
  Ciphertext becomes plaintext in place. Silently a no-op otherwise.
- **`git-push`** pushes the current branch as the user (`-u origin <branch>`);
  `--force-with-lease` only after a rebase, and **never on master**. Pushing master needs
  `admin`.
- **`git-merge <slug>`** is the one gate to master: fetch, `--no-ff` merge of
  `origin/user/<slug>`, clean abort on conflict, then push.

So a collaborator's work lands on master only through an admin's review. That is the
review gate the web must not bypass, and it is enforced by the floor rather than by
convention.

## 11 · The site

### 11.1 The app shell

`GET /` serves the whole shell; every other path renders **into a region of it**. Four
fixed regions occupy exactly the viewport — the page itself never scrolls; each middle
pane scrolls its own overflow.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ HEADER  eiπ+1=0 │ Solutions · Docs · Topics │ Actions │ ⌂ crumbs…      │ 🯅 │  fixed
├──────────────────────────────────────┬───────────────────────────────────────┤
│  LEFT PANE  (#content)                │  RIGHT PANE  (#ws)                    │
│  navigable content, htmx-swapped;     │  the solver PTY terminal over /ws     │  equal
│  deep-linkable; scrolls ↕ and ↔       │  persists across left-pane swaps      │  width
├──────────────────────────────────────┴───────────────────────────────────────┤
│ FOOTER   © · license · terms of use · acknowledgements                        │  fixed
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Header** — one control surface, identical on every page: the brand (→ `/`), primary
  nav, the **Actions** menu (page-specific verbs, always present even when empty), a
  **back arrow**, **breadcrumbs**, and the **user glyph** (Account, the terminal
  connect/disconnect item, Logout).

  The back arrow is not redundant with the browser's. The browser's back navigates the
  *document* and would take the terminal with it, so the pane keeps a history of its own
  and performs a swap, not a navigation.

  The terminal item is **one** entry, not two: it names the act it offers
  ("Disconnect terminal") and the dot beside it carries the state. The iframe reports
  `{euler: 'term-state', connected}` on every open and close, and the menu follows it —
  so a session that drops on its own never leaves the menu offering to disconnect
  something already gone.
- **Left pane `#content`** — the navigable region. Links `hx-get` a route and swap it
  here; `hx-push-url` updates the URL, so every view is deep-linkable.
- **Right pane `#ws`** — a same-origin **iframe** onto `/terminal`, its own document.
  This is what makes terminal persistence structural rather than a matter of discipline:
  htmx swaps, content-page JS, and history restores **cannot reach** another browsing
  context's document.
- **Footer** — © · license · terms · acknowledgements, all swapping into the left pane.
  Auth-tier pages (terms, change password) return a bare fragment on `HX-Request` so they
  render in `#content` without nesting a page.

`body` is a viewport-high grid (`auto 1fr auto`); the panes are equal (`1fr 1fr`)
independent scroll containers (`min-height: 0`). Controls never move between pages; only
pane content changes.

**One layout, signed out and signed in.** The auth service's pages are standalone public
documents on their own routes, but they are not a separate place: they render this same
`base.html` (its own `base.html` is gone, and its ChoiceLoader takes `web/templates`
first, then `site/templates`). The split is the two panes:

- the **left pane** is the start page — `_home.html`, the one partial both tiers render;
- the **right pane** holds the sign-in dialogue, standing exactly where the terminal will.

`subject` is the only switch. Signed out the header is *present and inert* (55% opacity):
the visitor sees the shape of the place before being let into it. The brand and the user
pill stay live — they are the two controls that still do something (home, and the way in),
and the pill reads as *empty*, a dashed ring, never as disabled. The start page's cards
keep their boxes and their copy, as `<span>`s with a padlock where the arrow goes, because
a visitor should see exactly what is behind the login. The solved count is **not** shown
signed out: the auth service has no clone and no `problems.json`, so it cannot know it.

The auth tier builds a `subject` from its session cookie (`shell_context` in `auth/app.py`)
purely so the header renders correctly on the two pages a signed-in visitor can still land
on — `/terms` and `/password`, both deep-link fallbacks. It is **presentational only**:
that service's routes gate on `session_identity`, never on it.

Signed out, `base.html`'s `shell_assets` block is overridden away: no htmx and no MathJax.
Nothing swaps and nothing carries TeX, and a login box has no business pulling a megabyte
of typesetter. `/about/license` and `/about/acknowledgements` sit behind `forward_auth`,
so the footer dims them signed out rather than offering links that bounce to `/login`;
`/terms` is an auth route and public, so it stays live.

**The README** is rendered below the cards on the start page, in both tiers. It comes from
the **packaged** copy — `setup.py`'s `build_py` hook copies the root `README.md` to
`solver/web/content/README.md` at build time (gitignored; root stays the source of truth),
and `pyproject.toml` ships it as package data. Both tiers read that copy, cached per
process: `euler-auth` runs from `/opt/euler` with `ProtectHome=true` and has no clone to
read, and the start page must say the same thing whatever branch a collaborator is on.
`/docs/readme` and `/about/readme` still read the clone's — that is the docs viewer's
contract (a contributor editing docs must see their own edit), not an inconsistency.

### 11.2 Visual identity

**The brand is Euler's identity, `e^iπ + 1 = 0`.** The glyph and favicon are its
geometric reading on the unit circle: the upper semicircle from `1` to `−1` (the rotation
by `π`) plus the unit segment from `−1` back to `0`, a two-stroke SVG in accent orange.
The wordmark is the formula itself, not the word "euler".

**Dark only.** There is no light palette and no theme control: the dark ground is the
design, not a preference. (There was a remembered slider; it was removed with the
signed-out redesign, along with `auth.css`.)

| token | value |
|---|---|
| `--bg` | `#0f1115` |
| `--surface` | `#171a21` |
| `--surface-hi` | `#1f2430` |
| `--border` | `#2a2f3a` |
| `--text` | `#e5e7eb` |
| `--muted` | `#9ca3af` |
| `--accent` | `#f97316` |
| `--accent-ink` | `#fed7aa` |

Detail colours are tokens too: grid heat (`--heat-1…5`), file git status, and a semantic
set kept separate from the accent — `--ok` / `--danger` for state pills and destructive
verbs, `--error-*` / `--notice-*` for the auth flashes.

**`site.css` is the site's only stylesheet**, loaded by both tiers, and Caddy serves it
from `/assets` *ahead of* `forward_auth` (`frontend.sh`) — so a signed-out page needs no
session to be styled. There is no app service in the path for static assets. (There were
two stylesheets, `site.css` and `auth.css`, duplicating the same tokens; collapsing them
is what makes one layout possible. The two form styles collapsed with them: `.auth-form`
is the one, and `.pane-form` is gone.)

Everything is self-contained and same-origin: no external fonts or CDNs, a system font
stack, vendored htmx and MathJax from `/vendor`. Statements and notes carry math as TeX
text (`$…$`); MathJax typesets on load and after every swap.

**The terminal pins its own dark**, in literal hex rather than the tokens. It renders the
*shell's own* output, and the shell paints with absolute xterm-256 indices chosen for a
dark terminal (near-whites like 254/247, 238 for rules). Its darkness is the shell's
constraint, not the site's choice — the site being dark-only means the two agree today,
but the pane must not start following a palette the shell's ANSI indices know nothing
about. The values are the dark tokens, so it reads as an embedded console, not a foreign
surface.

### 11.3 Writing style

The voice of pages the service *authors* — index copy, blurbs, status lines, not the
rendered guides themselves:

- **Never state the obvious.** No "click a link to navigate"; no restating what the
  reader is looking at.
- **Humour, lightly.** The register: "*Twelve guides stand between you and the next
  unsolved problem. Read one, ignore the rest, feel briefly invincible.*"
- **Intuitive and useful.** Every sentence either orients or enables; cut the rest.
- **Block boxes for items.** Enumerable things render as cards, two or three per row —
  not bullet lists.

### 11.4 Path ownership

| Owner | Paths |
|---|---|
| **Caddy-native / static** | `/healthz`, `/assets/*`, `/vendor/*`, `/favicon.ico` |
| **Auth service** | `/login`, `/register*`, `/reset*`, `/forgot`, `/password`, `/terms`, `/auth/*` |
| **Per-user service** | everything else, including `/ws` |

The static row is why one stylesheet is enough: `/assets/*` and `/vendor/*` are `handle`d
by Caddy *above* the `forward_auth` block, so the signed-out pages load the same
`site.css` as the shell with no session and no app service in the path.

The auth service's pages render the **shell** (`base.html`, `_nav.html`, `_home.html`, the
crumbs and actions partials) from `site/templates` and override none of it — the chrome
has one source of truth, not a copy that drifts. Its own `templates/` dir holds only what
is genuinely auth's: `auth_base.html` and the dialogues.

### 11.5 Routes

A **fragment** is what an `hx-get`/`hx-post` renders into `#content`; a **direct** hit on
the same path returns the whole shell with that pane pre-populated, so links are
shareable and reload-safe. **Writes always return a fragment**, never the shell.

| Method | Path | Renders | Floor |
|---|---|---|---|
| GET | `/` | the app shell; left pane = landing (`_home.html` + README), right pane = the `/terminal` iframe | reader |
| GET | `/terminal` | the right pane's standalone document: xterm.js + the `/ws` client | reader |
| GET | `/solutions/` | `problems.json` as 10×10 century grids + summary | reader |
| GET | `/solutions/{n}/` | statement, then test cases · results · files · notes | reader |
| GET | `/solutions/{n}/{filename}` | one problem file | reader |
| GET | `/docs/` · `/docs/{name}` | docs index (card grid) · a rendered doc | reader |
| GET | `/docs/file/{path}` | a doc-referenced repo file, from the readable roots only | reader |
| GET | `/topics/` · `/topics/{name}` | topics index · a topic page | reader |
| GET | `/about/{name}` | footer pages: `readme` · `license` · `acknowledgements` | reader |
| GET | `/account` | identity + the profile ladder, the credential panel, the password form | reader |
| GET/POST | `/edit/solutions/` | progress upload (empty buffer) → save | contributor |
| GET/POST | `/edit/solutions/{n}/{filename}` | file editor → save | contributor |
| DELETE | `/edit/solutions/{n}/{filename}` | delete a bare `.py`/`.c` → the problem-page fragment | maintainer |
| GET | `/ws` | the PTY WebSocket attach | reader |

**Canonical trailing slash.** Every GET path is canonical *with* its slash; a slashless
GET returns a **301**, so each view has exactly one URL.

The `/docs/file/` view may serve only the service's readable roots — `docs/`, `topics/`,
`solver/templates/`, `solutions/`, `README.md`, `LICENSE`, and the vendor README.

**Page chrome via out-of-band swaps.** Breadcrumbs and Actions are page-specific but live
in the fixed header, which htmx never re-renders — so every fragment response carries
them as `hx-swap-oob` alongside the pane content, and a full-page render places the same
partials directly. One source of truth per page: the handler supplies `crumbs` and
`actions`. Actions is filtered by the subject's profile, but **hiding is UX; the route's
floor is the boundary**.

### 11.6 Content pages

- **Landing, docs index, topics index** — a short hero over a **card grid**. The landing
  stacks its entry points one per row (Solutions · Docs · Topics · Terminal), then the
  **README** below them under a mono eyebrow — an eyebrow rather than a heading, because
  the README is the same page continuing, not a new section competing with the hero. The
  indexes list two or three per row, showing the filename as the first line and the
  markdown `#` title as the second, sorted by filename.
- **Account** — identity (email, and the slug that names the system user, home and clone
  that are theirs alone), then the **profile ladder**: the four rungs with theirs lit and
  the ones below it filled, because the ladder is cumulative and a reader who saw only
  their own rung lit would misread it. `LADDER` is the kernel's own tuple, so the rendered
  rungs cannot drift from the model the checks use. Then the credential panel (the
  per-user service's `/account/vault` fragment) and the password form. Changing a password
  lives here rather than in the user menu: it is an account thing, and the menu is for
  getting places.
- **Solutions** — the 10×10 century grids: square cells (and so square grids, via
  `aspect-ratio`), packed as many per row as fit (`auto-fill`), shaded by difficulty with
  the heat tokens, title and pct on hover.
- **Progress upload** — an **empty** paste buffer, because this is a *replace*, not an
  edit: the previous `.progress.html` is superseded wholesale, parse-or-reject before
  anything lands.
- **Problem** — statement first, then test cases · results · files · notes. Two off-site
  links on the meta line (projecteuler.net and the GitHub solution directory). Test cases
  render as a table, not raw JSON. Files flow horizontally, plain-text links, zero-size
  files hidden, each name coloured by its git status with the status spelled out in the
  hover title.

**Every off-site link opens in a new tab.** `site.js` stamps `target="_blank"
rel="noopener noreferrer"` on any link whose host is not ours, on load and after every
swap. It is a document-wide rule rather than per-link markup precisely because the
riskiest links are the ones we do not author — cached projecteuler.net statements, notes'
reference links. Following one in place would tear down the shell, and with it the
terminal.

**Rendered-doc links** are rewired for the shell: a `foo.md` cross-link becomes the
`/docs/` route; a repo-relative `../<path>` becomes the `/docs/file/<path>` viewer (so one
authored link resolves both on GitHub and in-app); every internal link gets `hx-*` so it
swaps the pane in place.

### 11.7 The save gate

The checks every write passes, in `solver/web/site/validate.py`: `.py` (auto-fix, then
flake8 over stdin), `.c` (scratch-dir compile against the runner header), `.json`
re-indent, and `.html` through **nh3**.

`notes.html` is served back and rendered, so writing it verbatim would be **stored XSS**.
nh3 runs a tailored allowlist on save — `article/h3/h4/p/ul/li/table/code/a`, keeping
`a`'s `class/target/rel/href`, MathJax `$…$` surviving as text — and **the sanitised
output is stored**, with the editor showing the diff. Store-clean rather than
reject-and-restore because nh3 always normalises (it adds `<tbody>`, rewrites `rel`), so
rejecting would bounce essentially every save.

nh3 gates what is **stored**; the CSP blocks what would **execute**. Independent layers.

Notes stay raw HTML rather than Markdown: they are semantic HTML5, as the AI convention
and the entire existing corpus already are, with math as MathJax TeX text. nh3 closes the
stored-XSS hole; there is no hand-authored-raw-HTML hazard left for Markdown to remove.

### 11.8 Content-Security-Policy

Every served page carries one, emitted by an app middleware (`solver/web/csp.py`, shared
by every rendering service) because a strict policy needs a **per-response nonce** — the
app that renders the page mints it and stamps it into both header and template.

```
default-src 'self'; script-src 'self' 'nonce-<per-response>';
style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self';
frame-ancestors 'self'; base-uri 'none'; object-src 'none'
```

**Scripts allow no `unsafe-inline` and no `unsafe-eval`, ever.**

Two entries are recorded exceptions rather than oversights:

- **`style-src 'unsafe-inline'`** — MathJax v3, CodeMirror 6, and htmx's indicator rules
  all inject stylesheets at runtime with **no nonce hook** (verified empirically: headless
  Chrome logged the violations, and the math rendered garbled under bare `'self'`). The
  residual risk is CSS injection only, and the markup paths that could carry it are closed
  upstream — Jinja autoescape, and nh3 strips `style` tags and attributes from stored HTML.
  Script execution remains nonce-gated.
- **`frame-ancestors 'self'`** — the shell frames its own `/terminal` document.
  Cross-origin embedding stays blocked.

`connect-src 'self'` needs **no `wss:` exception**: the terminal's WebSocket is
same-origin, and `'self'` covers the upgrade to the page's own host. Verified — headless
Chrome logs zero violations across the shell and the framed terminal with the socket live.
(CSP 3 says so; it was worth confirming because CSP 1 did not, and older engines required
listing the `wss:` origin.)

Since htmx uses `hx-*` attributes rather than inline script, it coexists with a strict
policy — but **avoid `hx-on:` handlers**, which do not.

## 12 · The web shell

The terminal is the front door: **every rung gets one**. What varies by rung is what the
shell *inside* it will run, not whether it exists. It is the full `solver` shell — lexer,
parser, interpreter, prompt-toolkit — not a curated command protocol, because reusing the
hardest proven code with authorization already enforced at registration beats inventing a
bespoke command surface.

Attach is gated on the `reader` floor plus a live session plus a one-time ticket. Inside,
the rungs diverge by the same decorator floors as everywhere else (§6.4): a `reader`
shell registers only the read commands and the shell's own safe AST expression evaluator
(no calls, no attribute access), so it runs no user code at all; `contributor` adds edit,
eval/benchmark, raw bash, the AI commands, and the git write verbs.

### 12.1 Lifecycle

**One persistent shell per user** (the manager keys by email), tmux-style: a second tab
attaches to the *same* shell. A single background drainer reads the PTY continuously into
a bounded replay buffer and fans output out to every attached socket, so the shell
survives disconnects and a reconnect redraws.

Its lifetime is decoupled from any socket and bounded by exactly four teardown paths:

1. **In-shell exit** (`exit` / Ctrl-D) — the drainer sees EOF and reaps.
2. **Logout** — the auth service, the only party that sees the event, POSTs a best-effort
   `/internal/logout {email}` to the user's socket. It can: `euler-auth` is in
   `euler-web` and the socket is `0660`. The endpoint is **socket-peer only** — Caddy
   routes `/ws` and nothing else to these services, so no browser can reach it.
3. **Revocation** — `users change`/`disable`/`remove` and password reset push the
   identical teardown. This closes the one real gap in "staleness is re-login": a
   *running* shell resolved its permissions at startup, and without the push a demoted or
   disabled account would keep its old authority until the process happened to die.
4. **Service stop** — `on_cleanup` closes every shell, and systemd's cgroup kill collects
   stragglers.

Plus hygiene, not security: a **detached-TTL reaper** closes a shell with zero attached
sockets for `EULER_WS_DETACHED_TTL` (default 24 h — generous on purpose, so a long
benchmark survives a closed laptop). Session *expiry* is deliberately **not** a teardown:
the owner remains an authorized user, re-attach demands a fresh login and a fresh ticket
anyway, and killing work on a timer would break the persistence contract.

The reasoning: attach is freshly vouched every time — a live session at the edge, a
one-time ticket at the fork — so the only residual risk a persistent shell carries is
stale authority *inside an already-running process*. The revocation push removes exactly
that, at its source, rather than having the shell tier poll for something it cannot
observe.

### 12.2 Two client-side subtleties

**The refresh guard.** A *full* page load (F5, address-bar entry, tab close) is the only
thing that can reach the terminal, and the iframe guards it with a `beforeunload`
confirmation armed while its WebSocket is open, disarmed on disconnect and on deliberate
exits (the shell posts `{euler: 'disarm'}` to the iframe before logout). The PTY itself
survives server-side regardless — the dialog protects the *scrollback and flow*, not the
process.

**The attach replay is drawn, never obeyed.** A reattaching terminal is sent the shell's
recent scrollback, which contains the *control sequences* of commands that already ran —
`show`/`edit`'s OSC 5379 among them. A client that acted on those again would hijack the
pane on **every page load**: deep-link to one problem and land on whatever the shell last
showed. So the server closes the replay with an explicit `{"replay":"end"}` text frame
(the raw byte stream cannot carry an in-band marker), and the client honours OSC only
after it — sequenced *through* xterm's write queue, since `write()` is asynchronous and
the bytes are still being parsed when the marker arrives. A monotonic token remains the
within-session guard.

## 13 · Security posture

The trust boundary is the **invite list** — named, trusted collaborators. These are the
risks accepted **by design**; each is a deliberate choice with its containment stated.

**A `contributor`+ login is host code execution.** A contributor can `edit` a solution and
`evaluate` it, which runs arbitrary Python on the host; `claude-solve` launches a headless
agent with host tool access. Gating `!` high would not contain this — the effective trust
boundary is *who receives which profile*, not the command policy. **Contained:** `reader`
(the default invite tier) is genuinely read-only, so a new invitee triggers no host
execution of user code. Every web session runs as that collaborator's **own** uid, in
their own `0700` home and clone, from the root-owned venv, loopback-only behind the
kernel egress firewall. A compromised session reaches *that user's* home — never the
operator's, never another user's. **Standing controls:** grant `contributor`+
deliberately, keep the invite list audited, keep `reader` free of every code-execution
command, do not widen the unit's sandbox or the per-user egress lock.

**A web session reads the private plaintext its user is authorized for.** Each instance
serves its own clone, and `solutions/private/**` is ciphertext at rest **until the
operator key-authorizes that person** (§9). Private-plaintext visibility is per-person and
revocable, orthogonal to the ladder. **What remains accepted:** compromising an
*authorized* user's session reads the private plaintext in *that user's* worktree — the
deliberate cost of a shared solver over an invited set. Per-user uids keep one
compromise out of every other tree, and the egress lock leaves no arbitrary off-host
exfiltration path.

**`admin` is web-reachable.** With the channel axis gone, an `admin` account signed in
over the web could run the highest-privilege operations. In practice the admin API will
not assign `admin` to a web identity (§6.3), so this requires an out-of-band root edit —
but nothing in the resolver caps it. **Why accepted:** the containment that matters is the
uid plus SRP plus the profile grant, not which keyboard the request came from. **Standing
controls:** keep `admin` assigned to the operator alone; the admin plane stays wheel-gated
under sudo; admin-floor commands never widen to lower rungs.

**A key-authorized user's uid holds master-key access.** From `user-authorize` onward their
uid can unwrap the master key: decrypt the full private corpus (including straight off
GitHub) and forge ciphertext. **Why accepted:** it is the product. A trusted collaborator
working on private solutions needs exactly this power, and proof-of-possession is the
cleanest form of it. The act is per-person, explicit, and revocable — never self-service,
and `key-rekey` re-wraps only to still-authorized keys. **Standing controls:** authorize
named, trusted people only; treat `enc-key.json` changes as audited events (they are
commits); rekey on any doubt.

**The vault is at-rest opacity only.** Encrypted at rest and opaque to a passive or honest
operator; **not** protected against a malicious active root (§8.3). Do not over-claim
"zero-knowledge."

**`eval`/`benchmark` run untrusted solution code as the user.** A solution file is
arbitrary code, executed in the user's own session — the same uid holding their unlocked
vault. A malicious solution can read its own runner's secrets: the session `VK`, their
Anthropic key, and, if authorized, the master key. **Why accepted:** the blast radius is
**the user themselves**, which is the normal property of any shell that runs untrusted
code as you; different uids keep it away from every other user and the operator, and
egress is still Squid-gated. Sandboxing `eval` in a lower-privilege sub-uid or namespace
is the standing future hardening.

### Regression guards

Sound controls — invariants, not open work. Weakening any of these needs a matching
decision recorded here.

- **SRP-6a** (`solver/web/auth/srp.py`): the password never reaches the server or disk;
  correct `PAD`, `u≠0` / `A,B mod N≠0` checks, `secrets.compare_digest` throughout;
  cross-tested against the browser client.
- **Anti-enumeration**: stable decoy salt/`B` for unknown emails at `/auth/challenge`;
  generic responses from `/forgot` and every invalid-token page.
- **Invite-only registration**: single-use, **hashed**, time-boxed link tokens plus a
  live-mailbox OTP; the account written is the invite's bound email, never
  client-supplied.
- **Remember-me**: selector\:validator with rotation-on-use, theft detection, and
  `HMAC(validator)` at rest.
- **Identity is unforgeable**: Caddy strips client `X-User`/`X-Profile`/`X-User-Slug` and
  routes on the slug `forward_auth` returns; the per-user instance refuses a request whose
  `X-User` maps to another slug; web shells prove identity by a single-use ticket, not
  env; the local admin fallback requires the checkout-owner uid.
- **Wheel-gated admin plane**: the admin socket is `0600` euler-auth-private; the token
  lives only in root-readable `auth.env`; `users` mutations run under sudo.
- **Secret hygiene**: auth state `0600`, euler-auth-only, off the operator uid; a user's
  `id`/`env` vault-encrypted at rest in their `0700` home; the session `VK` lives only in
  a `0600` uid-private tmpfs file whose *path* is exported — the key itself is never in
  any process environment; logout and reset remove it; no secrets in logs (auth access
  logs are disabled, since tokens travel in query strings).
- **Ciphertext by default**: a provisioned clone is born filter-unwired, so
  `solutions/private/**` rests as ciphertext until the deliberate `user-authorize`;
  `gitfilter install` verifies key access **before** wiring anything.
- **Master-key gate to master**: pushing `master` needs `admin`; force-pushing it is
  refused unconditionally; a collaborator's work lands only via the admin's `git-merge`.
- **Network posture**: only Caddy is network-bound; the app tier is loopback-only
  (systemd `IPAddressDeny` + host nftables); all egress — including every dynamic
  `euler-user-*` uid, enumerated by prefix — via the Squid allowlist.
- **Cookies**: `Secure; HttpOnly; SameSite=Lax`, site-wide.

## 14 · Operating it

Every service ships the same kit — `install` / `uninstall` / `upgrade` / `status`, config
generation, and a health probe that reports actually-serving rather than
"process exists". Because the units live in **root's** systemd and run as locked-down
`euler-*` users, lifecycle needs **`sudo`**.

### 14.1 Install

```bash
echo 'EULER_TLS_DOMAIN=euler.example.com' >> ~/.euler/env   # if not already set
make install-web    # frontend → egress → ddns → firewall → smtp → auth → user
```

Or per kit: `make install-frontend | install-egress | install-ddns | install-firewall |
install-smtp | install-auth | install-user`.

`~/.euler/env` is the **install-time authoring source of truth**, read by the installer
(repo owner + sudo), which deploys **scoped** runtime config into `/etc/euler`. That
scoping is the point: `euler-ddns` sees only the DNS credentials, `euler-smtp` only the
Gmail ones, and no runtime service ever reads the full file. It carries
`EULER_TLS_DOMAIN`, the DNS provider credential pair (default `NAMEDOTCOM_USERNAME` /
`NAMEDOTCOM_TOKEN`), `SMTP_ADDRESS` / `SMTP_APP_PASSWORD`, and the operator's own
`ANTHROPIC_API_KEY`. The provider is selectable via `$EULER_TLS_DNS_PROVIDER` (default
`namecom`; also `cloudflare`, `route53`, `godaddy`, `digitalocean`, `gandi`).

Register the first admin account with `users add`.

### 14.2 Redeploy versus upgrade

**`make redeploy-web`** is the everyday turnaround after a source change: it pushes new
code, templates, and static assets without touching identities, units, certs, or the
firewall. `auth.sh redeploy` reinstalls the repo into the shared `/opt/euler` venv,
`user.sh redeploy` bounces running instances so their sockets re-activate them against
the rebuilt venv, and `frontend.sh redeploy` refreshes `/etc/euler/web-content` plus the
Caddyfile and reloads the edge.

Reach for **`make upgrade-web`** only when identities, units, or the Caddy/acme packages
themselves change. Note that systemd units are re-laid by `user.sh upgrade`, **not** by
`redeploy` — a unit change needs the upgrade path.

`make uninstall-web` tears the stack down in reverse; the kits prompt before deleting
state.

### 14.3 Going public

Only needed for access beyond the LAN.

- **Router:** port-forward **TCP 443** to the host's LAN IP (no port 80 — DNS-01 needs
  none), and give the host a DHCP reservation so its LAN IP does not drift.
- **WSL2 mirrored mode → Windows Hyper-V Firewall**, from an elevated PowerShell:

  ```powershell
  New-NetFirewallHyperVRule -Name "WSL-Caddy-443" -DisplayName "WSL Caddy HTTPS" `
    -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' `
    -Protocol TCP -LocalPorts 443 -Action Allow
  ```

  Confirm the VMCreatorId with `Get-NetFirewallHyperVVMCreator`; requires `[wsl2]
  firewall=true` in `.wslconfig` (the default).
- **Dynamic DNS:** `euler-ddns.timer` runs every 5 minutes, PUTting the A record only when
  the public IP changes, using the same token as DNS-01. Being infra egress, it does not
  pass through Squid.

### 14.4 Renewal

acme.sh runs as non-root `euler-acme` on a daily timer; its `--reloadcmd` fixes the key
mode and reloads via Caddy's admin API. Renewal needs no DNS credentials re-supplied —
acme.sh saved the token in the cert `.conf` at issue time. Force one with `frontend.sh
renew`. Each kit's `status` reports unit + health; `frontend.sh status` also shows cert
expiry and `/healthz`.

### 14.5 Configuration summary

| Layer | Key config |
|---|---|
| Authoring source | `~/.euler/env` (repo owner reads; installer deploys scoped copies) |
| Edge | `/etc/euler/Caddyfile` (`0644`), `/etc/euler/tls/server.{crt,key}` (setgid, key `0640`), `/etc/euler/web-content` |
| Egress | `/etc/euler-proxy/{squid.conf,squid.allowlist}`; client `HTTPS_PROXY` in `/etc/euler/egress.env` |
| Firewall + relay | `/etc/euler/nftables.conf`; `/etc/euler/smtp.env` (`root:euler-smtp 0640`) |
| Auth | `/opt/euler/venv`; `/etc/euler/auth.env` (`root:euler-auth 0640`); `/var/lib/euler-auth` (`0600`) |
| Policy | `/etc/euler/authorizations.json` (`root:root 0644`) |
| Per-user tier | `/etc/euler/user.env` (no secrets); `/home/euler-user-<slug>/` (`0700`) |
| Sockets | `/run/euler/*.sock` (`0660 euler-<svc>:euler-web`); `/run/euler-adm/auth-admin.sock` (`0600`) |

### 14.6 Verify

1. `solver "users add you@example.com"` emails a 7-day invite; opening it walks Terms
   (scroll-gated) → OTP → set-password and lands on `/login?registered=1`.
2. Signing in never places the password in a request body. A tampered or expired token
   shows the generic page, and `/register` with no token is linked from nowhere.
3. An unauthenticated request to any gated path `302`s to `/login`; `/healthz` and
   `/assets/*` stay public.
4. `/forgot` for a nonexistent email returns the same generic "check your mailbox" page as
   a real one.
5. **Masquerade:** a forged `X-User` or `X-User-Slug` header is stripped at the edge, so
   the upstream sees only the `forward_auth` value and a user cannot reach another's
   socket; a bare `solver` run as a `euler-*` uid with no ticket aborts; the web-shell
   ticket is single-use, so a replay from a sibling's `/proc/<pid>/environ` is dead on
   arrival; and a ticket whose slug differs from the instance pin aborts.
6. **Egress:** `firewall.sh status` probes an allowed and a dropped destination per uid.
