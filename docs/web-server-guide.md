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
- [13 · Messaging](#13--messaging)
- [14 · Security posture](#14--security-posture)
- [15 · Operating it](#15--operating-it)

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
        │  User=<slug>                     │   200 + X-User + X-Profile + X-User-Slug
        │  serves this collaborator's      │   or 401 → /login
        │  content routes AND /ws          │
        │                                  │       ┌─────────┐  allowlist egress only
        │  ~/euler   their clone, branch   │──────▶│  Squid   │─▶ api.anthropic.com,
        │            user/<slug>           │       │ (egress) │   projecteuler.net,
        │  ~/.euler  their vault (0700)    │       └─────────┘   github, claude.com
        └───────┬──────────────────────────┘
                │         ┌─────────────┐  message spool: threads + read-state;
                └────────▶│  euler-msg  │  SO_PEERCRED identity, AF_UNIX only,
                          └─────────────┘  never routed by Caddy
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
| per-user app | `<slug>` (e.g. `ue0f4a1`) | `/run/euler/user-<slug>.sock` | one collaborator's content routes + `/ws` |
| admin plane | `euler-auth` | `/run/euler-adm/auth-admin.sock` (`0600`) | account mutations; never routed by Caddy |
| message spool | `euler-msg` | `/run/euler/msg.sock` | user↔staff message threads (§13) |
| msg admin plane | `euler-msg` | `/run/euler-msg/admin.sock` (`0600`) | staff verbs from the operator's terminal |
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
   `/etc/euler/web-content`, so pages reference `'self'` assets and the CSP holds. Both
   are served **`Cache-Control: no-cache`** — "keep it, but ask before using it". These
   paths are unversioned and their contents change on every redeploy, while the pages
   referencing them are rendered fresh on every load; with only Caddy's `ETag` /
   `Last-Modified`, browsers fall back to *heuristic* freshness and a deploy silently
   leaves new HTML being driven by old JS, for whichever users happen to hold a cached
   copy. That is not a theoretical failure — it is what made a reworked user menu's
   terminal toggle inert against the previous `site.js`. Revalidation costs one
   conditional request that the ETag answers with a 304.
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

Per-user uids are created dynamically at provision time and are named for the
collaborator's slug alone, so the generator enumerates them **by the `euler-user` parent
group** every provisioned uid joins — there is no name prefix left to match on — and
folds them into the drop. Because the chain is policy-accept, an un-enumerated uid would
reach the internet directly, bypassing Squid — which is why `provision` reloads the
firewall.

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
repo owner. The admin commands never touch these files; they call the service (§6.5).

| File | Purpose |
|---|---|
| `users.json` | SRP verifier DB: `{salt, verifier, name, terms_version, terms_accepted_at, created, disabled}` per email. `name` is the display name, used for git authorship. **No profile** — that lives in `authorizations.json`, resolved fresh at each login. Not to be confused with `/etc/euler/roster/users.json` (§6.3): this one holds the login secrets and is euler-auth's alone; that one holds public keys, is world-readable, and carries no address at all. |
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
| Per-user instance | the OS | a `<slug>`-named uid (in the `euler-user` group) whose `EULER_USER_SLUG` pin maps back to its own handed-down email |
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

**Service uids.** A service uid that is neither a ticketed web shell nor a properly
pinned per-user instance **aborts**. This is what stops a web shell from running `unset
SOLVER_TICKET; solver` to re-resolve itself into a different identity. Two things count
as a service uid: an infra `euler-*` account (by name), and a **member of the root-owned
`euler-user` group** — the per-user instances, whose uids carry no distinguishing name.
The group is what makes the check un-forgeable from inside a web shell: a shell cannot
add or remove its own membership, so it cannot demote itself into the local-terminal
plane. There is no assume-an-identity path: `SOLVER_USER` is display-only.

**The local terminal.** The profile is the `authorizations.json` `users`-map value for
the OS login. The **checkout owner floors to `admin`** when unlisted — you cannot lock
yourself out of your own checkout — but an explicit entry wins, so the operator can
deliberately run local at a lower rung. Anyone else with an entry-less real login gets
`contributor`.

The slug scheme is worth one note. `slugify` emits a `.`-bearing form
(`mercanther_gmail.com-3f9e97`) that **fails `useradd`'s `NAME_REGEX`**, so the system
slug used for uids, homes, sockets, and `X-User-Slug` is a stricter derivation:
`u` + a six-hex-digit hash of the normalised e-mail (`u0a68e0`), matching
`^u[0-9a-f]{6,16}$`. It **is** the unix account name — the uid, `/home/<slug>`, the
socket, the unit instance, and the `user/<slug>` branch all read the same, with no
`euler-user-` prefix in front of it. Two consequences are deliberate: the name is short
enough to stay well inside the system limit whatever the address, and it publishes
nothing about who the collaborator is (`/home`, `ps`, and the branch list are all
readable by the other collaborators). The e-mail remains the login identity; the slug is
the derived system identity, and the only way back from one to the other is to recompute
`system_slug` over the policy's identities — which is what `make status-web` does to
show each unix name with its e-mail alias.

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

### 6.2 The roster is not the policy

`/etc/euler/roster/users.json` (§6.3) carries a `profile` field, and it is a **mirror**.
Every rank comparison — in the shell, in every service, on every route — reads the file above
and only that file. The rule the roster is built to is *facts that verify themselves, or
nothing* — a public key seals or it does not — and **no decisions**. `users list` reports
where the two disagree; the host is what applies.

The `euler-maint` group that may write the roster is a **write-ACL, not a copy of the
ladder**: it grants "may record a public key and a date", never a profile capability. A
member who has since been demoted can therefore mislead a menu, and nothing else.

### 6.3 The roster (`/etc/euler/roster/users.json`)

Who exists and what public key they hold. It is **read by everyone and written by
maintainers**, which is exactly the shape its readers need: the registry it replaces was an
admin-plane read behind `sudo`, which the shell that most needs it — a maintainer's, over the
web — can never obtain, so `key-rekey` refused to rotate without it, `key-split` had to be
handed a public key by hand, and `msg send`'s recipient menu shrank to two words.

It spent one revision as a *tracked* file, which fixed the reading and broke the writing:
`users` is admin-gated and sudo'd, but `user-authorize` and `key-split` are **maintainer**
commands, so a maintainer's grant wrote the file in their own clone on their own branch, where
it reached nobody and collided at the next sync. `/etc/euler/roster/` is `root:euler-maint
2775` — setgid, so a file created there inherits the group — with the file at `0664`. The
*directory* carries the group because an atomic replace renames a temp file over the target
and so needs write permission on the directory; a group-writable file in a root-owned
directory would force truncate-and-rewrite, and a crash mid-write leaves an empty roster,
which reads as "nobody holds a key".

The floor is `euler-maint` and never `euler-user` or `euler-web` (which hold every
collaborator) for one specific reason: `public_key` is the only field here that is *used*
rather than displayed — a grant seals half the master key to it — so whoever can write it can
redirect a future grant to a key they hold. With host read access to the share that is the
whole master key, which is why the group must be people who already have it.

```json
{
  "version": 1,
  "users": {
    "u3f9a2c": {
      "public_key": "…", "scope": "web", "profile": "contributor",
      "invited": "…", "provisioned": "…", "key_issued": "…", "removed": null
    }
  }
}
```

Four properties, each load-bearing:

- **Keyed by slug, and no e-mail address anywhere in it.** `system_slug` already keeps
  addresses out of `/home`, the process table and branch names.
  The spool routes by box key and a box key *is* the slug, so a recipient can be named
  without publishing who they are.
- **Acts, not states.** `invited` / `provisioned` / `key_issued` / `removed` are what the
  operator did, dated when they did it, so nothing else can make them stale. Registration
  state and `disabled` stay on the host and are joined in at display time: a mirror of
  `disabled` reading `active` for a locked-out account is exactly the stale copy that gets
  trusted.
- **Two floors, one file, no sweep.** `users add` / `change` / `remove` write it as the
  operator; `user-authorize` / `key-split` write it as any maintainer, recording the key they
  just sealed to. Each verb writes both places it needs to — the host's SoR through the
  sudo'd admin CLI, and this file for what every rung must read without `sudo` — so there is
  no registration step to remember and no repair sweep to run. `users list` reports drift if
  they get out of step anyway.
- **Total reader.** Absent, mangled (conflict markers included) or from a future schema all
  read as *empty*, because every caller's fallback is to ask the host, and a roster that
  raised would break commands that used to work without it.

**No key material.** Half the master key lived here briefly, on the argument that a single
share of a 2-of-2 split is a uniformly random point and reveals nothing. True, and beside the
point: this repository is public, so a half anyone can clone is not a second factor. It now
lives at `/etc/euler/share.json` on the host — see the
[Secret Sharing Guide](secret-sharing-guide.md).

This file used to carry `profiles`/`grants`/`objects` — an `object:permission` grant
vocabulary whose real job was deriving per-path filesystem ACLs on a *shared* operator
tree. Per-user uids retired that entire layer: each collaborator is alone in their own
clone, so there is nothing to partition by path. A legacy-shaped file still loads; only
its `users` map is read.

### 6.4 Enforcement

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

### 6.5 Administration — the `users` command

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

**Every verb writes both places it needs to.** The host's system of record — profile in
`authorizations.json`, SRP state in the service's own store — through the sudo'd admin CLI,
and the roster (§6.3) for what every rung must read without `sudo`. There is
deliberately **no key-registration verb**: the public key `key-rekey` re-issues against is
recorded by the grant that issues one (`user-authorize`), so the two files stay in step by
construction rather than by a sweep somebody has to remember. `users list` reports it when
they have drifted anyway.

It holds *public* material only, so losing it costs a re-authorization, never access. An
account with no key in the roster loses access at the next rotation, which `key-rekey` names
before you confirm.

> The accounts that predate the roster were migrated once (August 2026): their acts dated
> from the registration record and the enc-key file's mtime, and the duplicate `public_key`
> column stripped from the auth service's own store. One store, one copy. The migration
> script was deleted with the commit that ran it — it was a migration, not a tool.
>
> The roster itself moved out of the repository shortly after, for the write-path reason
> above; `scripts/setup/auth.sh` (`deploy_roster`) lays down the group, the directory and an
> empty file, and seeds the group from everyone the policy already ranks maintainer or admin.

**A rotation publishes before it issues, and that order is load-bearing.** `key-rekey`
re-encrypts the tracked private tree under the new key, commits *only* `solutions/private`
(by pathspec — `git commit` otherwise sweeps in whatever else is staged) and pushes it to
`origin/master`, and only then sends anybody their payload. Publishing second would strand
the first person to act on their message: a rotation makes every earlier blob unreadable, so
the instant they take the new key their own `HEAD` stops decrypting, and *every* way out goes
through `HEAD` — `git stash` materialises it, so `git-sync` cannot even reach its merge.
They would be stuck being stale with no self-service repair. A push that fails is therefore
fatal to the rotation: nothing is issued, and re-running mints a further key, which costs
nothing because nobody ever received the last one.

**The receiving half re-homes the clone.** Even publishing first, a collaborator's own `HEAD`
predates the rotation, so `msg act` checks whether it still decrypts and moves the clone onto
the published tree when it does not — `git reset --hard origin/master`, the one worktree-wide
command that never has to materialise the unreadable `HEAD` on the way. Uncommitted private
edits are carried across as plaintext, collected *before* the new key is written, which is the
only moment they can be told apart from the rotation's own churn; plaintext is key-agnostic,
so they re-encrypt cleanly on the next commit. A clone whose `HEAD` *already* does not open —
wedged by an earlier rotation it never re-homed from — is asked nothing, because it has no
truthful answer: with the held key not matching `HEAD` every present private file cleans to a
different blob and reads as an edit. Unpushed **commits** stop it: reset would
orphan them, so the clone is left alone and the situation named. `git-sync` performs the same
re-home for a clone that wedged before any of this existed, minus the edits it can no longer
identify.

**Which side is unreadable says what to do.** A clone that has *not* yet been issued the new
key is perfectly coherent — its own `HEAD` opens under the key it holds — and it is
`origin/master` that it cannot read. Nothing local fixes that: the key is in the spool. So
`git-sync` fetches first, asks both questions, and **refuses before merging** when the
incoming blobs are the unreadable ones; merging anyway cost a live collaborator a filter
traceback *and* a half-applied merge that left a private file deleted in their worktree. The
login banner asks the same pair, so a stale clone is told how to take the key rather than the
generic "run `git-sync` to see why" — which, after a rotation, points at the one command that
cannot work. The instruction follows the channel: over the web it names the header's message
chip, whose key row is a **save**-labelled button, so nobody has to find and type a message
id; a terminal, having no header, gets `msg list` / `msg act <id>`.

**`add` has two paths.** An `@`-address is the **web** path: provision the collaborator
(§7), write the map entry, and mint an emailed invite — provisioning happens *before* the
invite, so there is never a dangling invite to a box with no shell. A bare **os-login**
is the **local** path: just the map entry, no invite, because a local login authenticates
by *being* that OS user.

**`admin` is assignable only to a local os-login.** The admin API validates a web
identity against `reader`/`contributor`/`maintainer`. The identity resolver, by
contrast, does *not* cap a redeemed ticket — so an email mapped to `admin` out-of-band
(a root edit of the policy file) would carry admin over the web. That is the accepted
posture in §14, not an oversight: containment for the highest-privilege operations is the
profile grant plus SRP plus uid isolation, with no channel backstop.

There is no reset verb — reset is self-service.

### 6.6 Command floors

Every command's declared floor is generated from the live registry into
[`authorizations.md`](authorizations.md) by `update-docs`. The shape of it:

| Floor | Commands |
|---|---|
| `reader` | `ls`, `show`, `results`, `test-cases`, `problems`, `progress`, `search`, `git-status`, `git-sync`, `git-filter`, `user`, `vault`, `msg` (own threads + send to staff), `?`/`echo`/`clear`/`pause`, `key-reconstruct` |
| `contributor` | `new`, `edit`, `evaluate`, `benchmark`, `compile-c`, `lint`, `mark`, `!`, `claude-api`, `claude-solve`, `costs`, `git-commit`, `git-push`, `git-hooks`, `git-identity` |
| `maintainer` | `summary` (rewrites the shared progress state), `gh-merge` (merges a solutions-only pull request), `msg send` to anyone but staff, `user-authorize` and `key-split` (grant enc-key access — the staff floor, so whoever receives a key request can act on it), `git-publish`, `update-usd-rate`, web file-delete |
| `admin` | `users` (the whole command, sudo'd), `key-rekey`, `host-authorize` / `host-unlock`, `update-docs`, `update-models`, `pip-upgrade`, `sys-setup` |

Two floors deserve their reasoning. **`!` (raw bash) sits at `contributor`**, not admin:
in the per-user model a shell escape grants nothing that `evaluate`'s arbitrary Python
did not already, and it is the user's own uid sandbox either way. **AI commands sit at
`contributor`** because the credentials are the user's *own* Anthropic key from their own
vault — it is their spend, not the operator's.

## 7 · The per-user tier

One systemd template instance per collaborator — `euler-user@<slug>.service`,
`User=<slug>` — serves **both** that user's content routes and their `/ws`
shell, all operating on their own `~/euler`. Caddy routes every request for a user to
their one socket by `X-User-Slug`.

Each instance is **born as the right uid**: no process changes uid, nothing runs as
root, no setuid anywhere. It is **socket-activated** (`euler-user@<slug>.socket`), so
idle invitees cost nothing and systemd starts the instance on first attach.

Content and shell are one service because the isolation boundary is now the uid. Splitting
them would separate two things that already share a sandbox — one service kind, one
socket per user.

```
home  /home/<slug>/                                (0700, uid-private)
  ├─ euler/          their repo clone — content, branch user/<slug>
  │    └─ solutions/private/**   ciphertext until enc-key authorized (§9)
  └─ .euler/         their vault (§8)
       ├─ id         their X25519 private key, encrypted under the vault key
       ├─ env        their ANTHROPIC_API_KEY etc., encrypted
       └─ vault      {salt, iterations, wrapped_vk}
```

Nothing in that directory is a password. A password at rest beside the ciphertext it
unlocks hands it to exactly the reader the encryption exists to stop, leaving the 0700
home as the only real protection — which is the thing the vault is meant to improve on.

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

1. create the system user `<slug>` (in the `euler-user` parent group) and its `0700`
   home at `/home/<slug>` — an existing account of that name is **never adopted**, since
   the slug is a bare name in the shared login namespace;
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

**Repair** — `sudo bash scripts/ops/reset-user.sh <slug>` fetches and hard-resets one
collaborator's clone to origin/master, as that user. It exists because a clone can reach a
state its owner cannot leave with the verbs their profile has. `git-reset` is at `reader`
now, so a branch merely *ahead* of origin/master is self-service — but it is `--soft` by
design, which is exactly why it is not the answer here: a conflicted merge or a
half-checked-out worktree needs `--hard`, and no rung is given that. It discards
their local commits and uncommitted changes — that is the point, and it prints what it is
about to destroy and asks first. It runs git **as them**, never as root, because
root-owned objects in their home turn one wedged clone into a permanently wedged one. It
also passes `/etc/euler/egress.env` through explicitly: the host is default-deny outbound
and Squid is the only route to github.com, which the services get via `EnvironmentFile=`
and a `sudo -u` shell inherits not at all — without it the fetch fails at DNS rather than
at the network. If
the reset fails decrypting `solutions/private` — their vault is unlocked only inside their
own session, and a `sudo -u` shell has none — `--no-filter` resets with the filter not
required, leaving ciphertext for their own `git-filter install` to decrypt in place.

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
- **Terminal** — `$EULER_VAULT_PASSWORD` if the operator exported one (a script, CI, an
  unattended run), otherwise the shell **asks**, once, at startup
  (`solver.crypto.keys.unlock_session`) and writes the tmpfs file its children inherit.
  There is deliberately **no password file**: the earlier `~/.euler/user_pass` made the
  terminal vault ceremony — anyone who could read the ciphertext could read the password
  next to it, so encrypting bought nothing over the 0700 dir that was already there.

  The asking has to happen in the shell, at startup, because the readers that need `VK`
  are *subprocesses* — the git clean/smudge filter above all — with no terminal and a
  stdout that belongs to git. `solver.crypto.vault` is on that path and therefore never
  prompts; every interactive part lives in `solver.crypto.keys`. A declined or wrong
  password is not fatal: the shell runs locked, and the private solutions and `claude-api`
  are what stay unavailable.

  **Only the terminal is ever asked** — `main.py` gates the startup unlock on
  `subject.channel`. On the web the vault is the browser's job by design (it derives `PK`
  and the service writes the key file *before* forking the shell), so a web shell that
  stopped to ask would be routing through the server the one secret that deliberately
  never goes there — and, on a locked vault, would stall every attach behind a prompt the
  user cannot see. The explicit `vault unlock` command still prompts on any channel: that
  one the user asked for.

  **A session removes the key file it created, and only that one.** `write_session_key`
  mkstemps one file per unlock, so without cleanup they accumulate for the life of the
  tmpfs and a `VK` outlives the shell that made it — "locked" then means nothing until
  logout, since anything running as that uid can lift a working key off disk without the
  password. `keys.unlock_session` therefore unlinks its own file at exit. The distinction
  is **ownership**, and it is the whole point: on the web path the per-user service writes
  the key file and *shares* it across every shell that user has open, so a shell that
  cleaned up an inherited file would lock the others — and the service's own session — out
  mid-flow. A file we merely found is never ours to remove. (Best-effort: SIGKILL runs no
  handler. This bounds the pile to live shells, not to every shell that ever ran.)

  One `mkstemp` per session is deliberate, not an oversight to "fix" with a single stable
  path: concurrent shells would then share one filename, and the first to exit would unlink
  it out from under the rest.

  The installers (`scripts/setup/*.sh`) read the same encrypted `~/.euler/env` for the
  deployment's authoring config, through `scripts/setup/authoring_env.sh` →
  `python -m solver.crypto.readenv`, which returns the same dotenv lines whether the file
  rests as plaintext or ciphertext — so a kit works on both sides of `vault init`.

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

- **Each user has their own X25519 keypair**, and their own **enc-key file**:
  `~/.euler/enc-key.json`, two records — `verify`, and the master key wrapped to their public
  key. Machine-local, `0600`, beside the private key that opens it. Nothing about key material
  is in the checkout, committed, or pulled.

  It was tracked until v1.6.0: `keys/enc-key.json`, every authorised key, distributed by git.
  That put per-machine key material into shared state and everything painful followed — a
  rotation dirtied a tracked file, `sync.sh` stashed and popped it around the merge, the pop
  conflicted with the authorised copy coming the other way, and the markers left the JSON
  unparseable, which every reader takes for "not authorised". A reader could not even repair
  it (`git-reset` was contributor-floored then; it sits at `reader` now). It also needed an
  attribution map, a purge verb, a
  machine-local overlay and a repair path in `git-sync` — all to manage a sharing nobody
  wanted.

- **Issuing is a deliberate staff act**, never self-service — it grants decryption of the
  *whole* private corpus, so `user-authorize` sits at `maintainer`: the floor that receives a
  key request is the floor that can act on it. The flow: the user runs `user`, which files a
  request through the message spool (§13) carrying their public key; a maintainer runs
  **`user-authorize <message-id>`**, which wraps the master key to that public key and sends
  the payload back as **its own message**; the user runs **`msg act <id>`**, which writes their enc-key
  file and wires the filter. **The distribution channel is the spool**, and the payload
  travels through it for the same reason the old file could sit in a public repo: without
  their private key it is inert.

- **The message id, not the key.** `user-authorize` takes either — they are told apart by
  shape (64 hex is a key, 16 is a thread id) — but the message form is the one to reach for:
  the key comes out of the request and the **requester comes from the thread's author**, which
  the spool resolved from `SO_PEERCRED` when it was filed and which no sender can dress up as
  somebody else. It refuses rather than guesses (the subject must be the key-request one, the
  body must hold exactly one hex token) and asks before granting. The worked request is
  dismissed once the grant is delivered.

- **Taking a key proves before it writes.** The subject must be the key-issue one, the payload
  must unwrap with *this* machine's private key, and its `verify` must decrypt to the known
  text. Only then does it replace the file — which may be the only thing between this machine
  and the whole private tree, so a mistargeted or corrupted payload has to fail *before* the
  write, not be discovered after it.

- **A rotation needs nobody.** `user --regen` mints a key pair and re-wraps the master key to
  it in place, because the file is this machine's alone. A request is filed only when the
  master key cannot be loaded at all — a first run, or a rotation whose carry failed. A locked
  vault never reaches that path: the private-key persist refuses first, so nobody is asked to
  re-issue to somebody who already holds the key.

- **Revocation is `key-rekey`** (admin), and it is the only thing that revokes. It rotates the
  master key, writes the operator's own file first (a rotation that fails half way must still
  leave the operator able to decrypt the tree it just re-encrypted), re-issues by message to
  every `public_key` on the roster (§6.3), and re-encrypts the private tree. An account with
  no registered public key cannot be re-issued to and is **named before you confirm** — that
  person loses access at this rotation, which is sometimes the intent and must never be a
  surprise.

- **The operator's own terminal cannot reach the spool**, by design: `/run/euler/msg.sock` is
  `euler-web`-only and the operator's uid deliberately is not. Both directions therefore go
  through the sudo plane (`solver.web.msg.client`), which is why a rotation or a grant may
  prompt for a password and a collaborator's own commands never do.

`user-authorize` and `key-rekey` never need a *user's* private key, so the vault never
interferes with enrollment or rotation. A user can have a working vault and no master-key
access at all — their pubkey simply is not in `enc-key.json`.

The account page's public-key row states exactly that, because "am I authorized?" is the
only question the row exists to answer: it reports **can / cannot decrypt** from an actual
`read_master_key()` — the unwrap *and* the verify, not the presence of a file — and shows
the hand-it-to-an-admin instruction **only** when the answer is *cannot*. An authorized
user has already done it, and being told again reads as though it had not worked. Every
failure mode collapses to one answer here (no keypair, a locked vault, no entry in
`enc-key.json`, a key that no longer unwraps after a `key-rekey`): not yet.

## 10 · Git

Git is **native** in the user's own clone — there is no broker, and nothing proxies it.
`git-status`/`git-sync`/`git-reset` sit at `reader`; `git-commit`/`git-push`/
`git-hooks`/`git-identity` at `contributor`; `gh-merge` at `maintainer`; `git-publish` at
`admin`.

`git-reset` is the one ref-moving verb at `reader`, and it earns it by what `--soft` does
*not* do: it keeps the working tree and makes no commit, so it can neither destroy work nor
put anything on master. The blast radius that floors every other write verb is empty here,
while the contributor floor stranded the rung least able to help itself — a reader cannot
commit their way out of a clone that has drifted ahead of origin/master.

`git-commit` is the **one** commit verb: what it stages is named by its targets
(`solution`, `solutions`, `docs`, `topics`, `update`) rather than by a command per body of
work, and `--amend` folds into HEAD instead of a second verb. `gh-merge` is the **one**
merge verb, and it reads from the same table: its allowlist is the union of those targets,
so a pull request may carry whatever `git-commit` could have staged — several commits,
spanning several targets — and one file outside it refuses the whole request. There is no
one-tree rule and no per-body-of-work gate.

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
  `admin`. It then **opens the branch's pull request** onto master (`gh pr create`, the
  same shape as `scripts/git/publish.sh`): landing on master needs `gh-merge merge`, so the
  PR is how a collaborator actually asks for their work to land, and a branch sitting on
  origin that nobody has been asked to review is not delivered work. Idempotent — a
  branch already under review has its URL reported rather than a second PR opened, so
  re-pushing as the branch grows keeps working and the open PR picks up the new commits.
  Skipped on master, on a branch level with origin/master (nothing to review), and with
  `--no-pr`.
- **`gh-merge`** is the one gate to master: `list` shows what is waiting, `merge <number>`
  squash-merges it. **A pull request must sit wholly inside `solutions/` or wholly inside
  `topics/`** — anything outside is refused, and a branch spanning both is asked to become
  two pull requests (one review is of one kind of work),
  and that gate is what puts the command at `maintainer` rather than `admin`: merging a
  branch of solutions or topic articles is reviewing content, but a branch that also
  edits the framework,
  the scripts, or the keys is asking for something else, and belongs to an admin reading
  it on GitHub. The file list is read from the pull request (`gh pr view --json files`);
  a list that cannot be read refuses the merge rather than passing for an empty one.

So a collaborator's work lands on master only through a maintainer's review, and only
when it is solutions. That is the review gate the web must not bypass, and it is enforced
by the floor plus the scope check rather than by convention.

The merge is a **squash**, which rewrites the branch's commits into one on master. The
collaborator's next `git-sync` absorbs that: the rebase drops the now-duplicate commits
(git matches them by patch-id) and the prune drops the merged branch, provided the repo
deletes head branches on merge. Both halves are needed — without the prune, the deleted
branch lingers as a stale `origin/user/<slug>`; without auto-delete, there is nothing to
prune and the old branch shadows the next push.

## 11 · The site

**Importing this package must stay free.** `solver/web/site/__init__.py` re-exports nothing:
the content service's app, its `gitstate` reader and, through that, `solver.crypto.wire`
are reached by naming the submodule, never by importing the package. The auth service reads
exactly one module from here (`content`, for the start page's README), and it is the
untrusted-input surface that holds no key material — so it must not acquire the crypt
filter's configuration as a side effect of an import.

That was not hypothetical. The package used to re-export `build_app` for convenience, which
made `from solver.web.site import content` execute the whole content app. It stayed invisible
while the crypto package invented a repo root whenever it could not find one; the moment that
started refusing (§ Git), the auth service — which has no `EULER_REPO_ROOT`, because it needs
no working tree — raised at import, never signalled readiness under `Type=notify`, and sat in
`activating`. Caddy authenticates every request through it, so the site went down with it.
Nothing had ever imported those names from the package.

### 11.1 The app shell

`GET /` serves the whole shell; every other path renders **into a region of it**. Four
fixed regions occupy exactly the viewport — the page itself never scrolls; each middle
pane scrolls its own overflow.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ HEADER  eiπ+1=0 │ Solutions · Docs · Topics · Terminal │ Actions │ ⌂ crumbs… │ ❯● │ ⑂ main │ 🯅 │
├──────────────────────────────────────┬───────────────────────────────────────┤
│  LEFT PANE  (#content)                │  ┌ solver terminal ─── ● Connect ─ ─┐ │
│  navigable content, htmx-swapped;     │  │ the solver PTY terminal over /ws │ │  equal
│  deep-linkable; scrolls ↕ and ↔       │  └ persists across left-pane swaps ─┘ │  width
├──────────────────────────────────────┴───────────────────────────────────────┤
│ FOOTER                       © · license · terms · acknowledgements │▭ terminal│  fixed
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Header** — one control surface, identical on every page: the brand (→ `/`), primary
  nav, the **Actions** menu (page-specific verbs, always present even when empty), a
  **back arrow**, **breadcrumbs**, the **terminal chip**, the **git chip** (§11.9), and
  the **user glyph** (Account, Logout).

  The back arrow is not redundant with the browser's. The browser's back navigates the
  *document* and would take the terminal with it, so the pane keeps a history of its own
  and performs a swap, not a navigation.

  The terminal chip and git sit inside `.app-who`, before the user glyph: `margin-left:
  auto` pushes that group right, and both belong on the *identity* side of the gap — they
  are state about **your session** and **your clone**, not about the page in the pane.

  **Connect/disconnect lives on the terminal window's own titlebar** (§ Right pane), next
  to hide: the session is a property of that window, and a control on the thing it
  acts on needs no explaining. It is **one** entry, not two, and it is **just the dot** —
  state and act in one mark, sized to the hide button beside it. No verb: a word in a
  1.6rem titlebar competes with the terminal's own name, for a control whose two states a
  colour already tells apart. What it will do is its `title`, which is also its accessible
  name and which `site.js` flips with the state. The user menu carries no terminal item at
  all; it is for getting places.

  The header's **terminal chip** reports **both** of the terminal's states, because they are
  independent and either one explains a shell that is not answering: the **session**
  (connected/disconnected) as the dot's colour, and **layout** (visible/hidden) as a slash
  struck through the glyph. The tooltip says both in words (`terminal — connected, hidden`).
  It exists because the titlebar can be hidden away (§ Footer), and the one thing that must
  never become unreadable is where the session stands.

  **And it offers the act for each.** The chip used to report only, with every control on
  the terminal window's own titlebar — which is exactly where they are unreachable in the
  state a person most needs them: hide the window and the titlebar goes with it, leaving the
  header saying "hidden" beside no way to bring it back but the nav's Terminal item. It is
  now a `<details class="menu">` on the same chassis as messages, git and the user pill, with
  a row per state: **connect/disconnect** and **hide/show**. The titlebar's controls are
  unchanged and stay the closest ones to hand while the window is there.

  Both rows carry the attributes `site.js` already dispatches on, so the panel added no
  wiring: `[data-term-toggle]` for the session, `[data-term-hide]`/`[data-term-show]` for the
  layout. The session row is **one** control that flips (the act on offer is always the
  opposite of the state, and `site.js` writes its label, title and accessible name from the
  same string), while hide and show stay **two** single-purpose controls — `site.js`'s
  invariant, so neither can lie about a state it did not read. They read as one flipping row
  because CSS shows whichever applies (`body.ws-hidden`), which keeps both the invariant and
  the single row a person expects.

  The chip is deliberately **not** `.term-menu`. That class marks a menu whose verbs type
  into the shell, which `site.js` dims when the socket is down — and Connect is precisely
  what someone looking at a disconnected chip came for.

  A terminal **control** is any `[data-term-toggle]` carrying a `[data-term-dot]` (its
  title and accessible name are painted, so a control needs no text of its own); a
  **readout** is any `[data-term-status]`. The iframe reports
  `{euler: 'term-state', connected}` on every open and close and `site.js` paints all of
  them from that single state, so the titlebar's toggle, the header's chip and the git
  panel's offline note cannot disagree — and a session that drops on its own never leaves
  a control offering to disconnect something already gone. They render **disconnected**
  and are painted on load: markup is served before the socket has said anything, and a
  control that claims a live session it has not been told about is a claim nothing can
  correct.
- **Left pane `#content`** — the navigable region. Links `hx-get` a route and swap it
  here; `hx-push-url` updates the URL, so every view is deep-linkable.
- **Right pane `#ws`** — a same-origin **iframe** onto `/terminal`, its own document.
  This is what makes terminal persistence structural rather than a matter of discipline:
  htmx swaps, content-page JS, and history restores **cannot reach** another browsing
  context's document.
- **Footer** — right-aligned: © · license · terms · acknowledgements, all swapping into
  the left pane (auth-tier pages — terms, change password — return a bare fragment on
  `HX-Request` so they render in `#content` without nesting a page), and — only while the
  terminal is hidden — its **window** at the very end.

  Nothing is reserved for it: it is `display: none` while the terminal is visible, so the
  documents hold the right edge on their own and hiding it pushes them left by exactly
  the window's width. What appears there is a window collapsed to its titlebar — window
  figure · name · show glyph — so what it is and what clicking it does are the same
  picture.

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
and the pill reads as *empty*, a dashed ring, never as disabled. The section strip's tiles
keep their boxes and their copy, as `<span>`s with a padlock where the arrow goes, because
a visitor should see exactly what is behind the login. No count is shown signed out —
neither the solved count in the lede nor the strip's data lines: the auth service has no
clone and no `problems.json`, so it cannot know them, and the tiles fall back to prose.

The auth tier builds a `subject` from its session cookie (`shell_context` in `auth/app.py`)
purely so the header renders correctly on the two pages a signed-in visitor can still land
on — `/terms` and `/password`, both deep-link fallbacks. It is **presentational only**:
that service's routes gate on `session_identity`, never on it.

Signed out, `base.html`'s `shell_assets` block is overridden away: no htmx and no MathJax.
Nothing swaps and nothing carries TeX, and a login box has no business pulling a megabyte
of typesetter. `/about/license` and `/about/acknowledgements` sit behind `forward_auth`,
so the footer dims them signed out rather than offering links that bounce to `/login`;
`/terms` is an auth route and public, so it stays live.

**A README summary** is rendered below the strip on the start page, in both tiers — an
*extract*, not the whole README, closed by a "read the full README" link (in-app to
`/docs/readme` signed in, out to GitHub signed out). It comes from the **packaged** copy
`solver/web/content/home-summary.md`: a tracked, generated file that the `update-docs`
command rebuilds from the slice of the root `README.md` between its `<!-- HOME:START -->` /
`<!-- HOME:END -->` markers (root stays the source of truth), shipped as package data via
`pyproject.toml`. Both tiers read that copy, cached per process: `euler-auth` runs from
`/opt/euler` with `ProtectHome=true` and has no clone to read, and the start page must say
the same thing whatever branch a collaborator is on. `/docs/readme` and `/about/readme`
still read the clone's full README — that is the docs viewer's contract (a contributor
editing docs must see their own edit), not an inconsistency.

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

That vendoring has to include what MathJax fetches **at runtime**: its woff fonts, and the
TeX extension for every macro outside the bundle's default packages —
`<bundle root>/input/tex/extensions/<pkg>.js` for `\color`, `\pu`, `\style`,
`\boldsymbol`, `\enclose` and `\unicode`. Same-origin, so `script-src 'self'` admits it;
missing, it 404s and the `noundefined` package renders the macro as its own name in red —
the "`\color` in red" a cached statement showed before the extensions were vendored. The
set that ships is the set the cached statements actually use
(`solver/web/content/vendor/README.md` lists it, and how to re-scan).

**Those six are preloaded, and the swap re-typeset is chained.** Both halves are about the
same failure, and it took two goes to see it whole. MathJax's `autoload` fetches a package
*on first use* — in the middle of a typeset — and `site.js` used to fire
`MathJax.typesetPromise()` behind a bare `if (window.MathJax && MathJax.typesetPromise)`
guard. That guard loses on either side of its race with the deferred bundle: too early
MathJax is still the plain config object and the swap is never typeset at all; a moment
later `typesetPromise` exists but startup has not added the packages, so the typeset runs
against a half-configured TeX input and every non-default macro renders as its own source.
Reaching a problem by the terminal's `show` did exactly that, printing
`\color[RGB]124, 192, 255` mid-sentence, while a refresh of the same URL looked perfect —
which is what made it read like a content bug rather than a wiring one.

So `loader.load` fetches the six at startup, and the swap re-typeset waits on `mathReady`,
resolved inside MathJax's own `pageReady` (after the loader *and* the initial typeset).
Later swaps queue behind their predecessor, which MathJax requires — concurrent typesets on
one document are unsupported, and it is the *rapid* sequence (`show 238`, `show 91`,
`show 238`) that made this reproducible at all: a single swap always recovered. Reproduced
in headless Chrome against the real vendored bundle, failing before the change and clean
after, and pinned by `tests/test_web_verbs.py::MathJaxWiringTests`.

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
| GET | `/shell` | the Terminal item's target page: the four start tiles + `docs/user-guide.md` | reader |
| GET | `/solutions/` | `problems.json` as 10×10 century grids + summary | reader |
| GET | `/solutions/{n}/` | statement, then test cases · results · files · notes | reader |
| GET | `/solutions/{n}/{filename}` | one problem file | reader |
| GET | `/docs/` · `/docs/{name}` | docs index (card grid) · a rendered doc | reader |
| GET | `/docs/file/{path}` | a doc-referenced repo file, from the readable roots only | reader |
| GET | `/topics/` · `/topics/{name}` | topics index · a topic page (`{name}` may be a nested `folder/page` path) | reader |
| GET | `/about/{name}` | footer pages: `readme` · `license` · `acknowledgements` | reader |
| GET | `/account` | identity + the profile ladder, the credential panel, the password form | reader |
| GET | `/git` | the header git chip's contents — the refresh the shell, the menu-open and the poll ask for (§11.9) | reader |
| GET | `/messages` | the header's message chip alone — count, rows, verbs (§13) | reader |
| GET/POST | `/edit/solutions/` | progress upload (empty buffer) → save | contributor |
| GET/POST | `/edit/solutions/{n}/{filename}` | file editor → save | contributor |
| DELETE | `/edit/solutions/{n}/{filename}` | delete a bare `.py`/`.c` → the problem-page fragment | maintainer |
| GET | `/ws` | the PTY WebSocket attach | reader |

**Canonical trailing slash.** Every GET path is canonical *with* its slash; a slashless
GET returns a **301**, so each view has exactly one URL.

The `/docs/file/` view may serve only the service's readable roots — `docs/`, `topics/`,
`solver/templates/`, `solutions/`, `README.md`, `LICENSE`, and the vendor README.

**Page chrome via out-of-band swaps.** Breadcrumbs, Actions and the git chip live in the
fixed header, which htmx never re-renders — so every fragment response carries them as
`hx-swap-oob` alongside the pane content, and a full-page render places the same partials
directly. One source of truth per page: the handler supplies `crumbs` and `actions`, and
the git middleware supplies `git`. Actions is filtered by the subject's profile, but
**hiding is UX; the route's floor is the boundary**.

**Page-specific verbs go in the Actions menu, never on the page.** A page's controls —
Edit, Save, Delete, a "show drafts" toggle, a topic's Write / Rewrite — belong in the
header **Actions** menu, built as the handler's `actions` list, not rendered as links or
buttons in the content pane. One place to look for what a page can do, one rendering path,
and the pane stays the content. An Action is `{label, kind, …}`: `kind` is `get` (an hx
pane-swap), `post` / `delete` (an hx mutation), `submit` (submit the pane's editor form),
or **`term`** (type its `command` into the web shell via `data-term-cmd`, the same
one-execution-path move the git chip's verbs make — so the command's own `requires()` is
the real boundary). **The back-step is the breadcrumb trail** in the header (and the `←`
control beside it); a page carries no "← docs" / "← topics" link of its own.

### 11.6 Content pages

- **The five index pages — home · solutions · docs · topics · terminal — are one layout.**
  From a distance they are the same page: a hero, the **section strip**, the **divider**,
  and then the page's own content. What changes below the divider is all that changes.

  ```
  KICKER · H1 · lede

  ┏━━━━━━━━━━━┓┌───────────┐┌───────────┐┌───────────┐   the section strip:
  ┃π Solutions┃│§ Docs     ││λ Topics   ││❯ Terminal │   the current one lit,
  ┃311 of 1007┃│16 guides  ││859 of 1007││● connected│   each carrying live state
  ┗▔▔▔━━━━━━━━┛└───────────┘└▔▔▔▔▔━━━━━━┛└───────────┘

  GUIDES ────────────────────────  filter…          16   the divider
  ┌───────────┐┌───────────┐┌───────────┐┌───────────┐
  │ the page's own tiles, grids or prose              │
  ```

  **The hero's three slots say three different things, in the same order on all five
  pages.** The **kicker** is the page's one witty line — an aphorism, lowercase, no full
  stop; it is *not* the section name, which the header nav and the strip already say twice.
  The **h1** is the plain title (`Solutions`, `The guides`, `The mathematics`, `The solver
  shell`; on home, the site's own name). The **lede** is the fact worth knowing, told with
  the same voice as the kicker — a count and what is still ahead of it, never a restatement
  of what the content below already shows.

  **The section strip** (`_sections.html`, one definition for all five pages) carries live
  **counts**, not prose: it repeats the header's nav on every page, so it has to say
  something the header cannot — how much is solved, how much is written, whether the shell
  is up. The Terminal tile's line is the socket itself, painted by `site.js` from the
  iframe's report (`[data-term-dot]`, `[data-term-state]`), never asserted by the server.
  The counts come from `content.section_state` — `problems.json`, a `docs/` scan, and the
  **union** (not the sum) of the problems the finished topic articles reach.

  It is the same tile object as the grids below it, in a **quieter register**: flat on the
  page ground, no lift on hover, because chrome does not move and content does. Two grids
  of the identical object would read as one field of eight. The page you are on is the one
  filled tile on the strip, wearing an inset accent edge and, in the corner slot, a
  you-are-here mark instead of the `→` — there is no journey to offer to the page already
  in the pane. The strip is exempt from the filter for the same reason.

  **The divider** (`_divider.html`) is the `.subrule` device — a mono label trailed by a
  hairline — doing three jobs: it names the region below, it **narrows** it, and the count
  at the end of the rule is the count of what survived. Typing hides the cards that miss
  and folds away a folder heading whose whole grid went; on the century grids it **dims**
  instead, because a cell's position is what says which problem it is and hiding the misses
  would renumber the grid under the reader. The query is remembered per section for the
  browser session (`sessionStorage`), so returning to the topics resumes the narrowed view
  without arriving pre-typed over the guides. The start page has prose below its rule and
  nothing to narrow, so it states that instead of offering a dead box.

  `/shell` is that layout with the **docs index cut to four** (`content.SHELL_DOCS`, the
  guides worth having at a prompt) and then the **command catalogue** itself — the
  generated `docs/commands-catalogue.md`, rendered in place, which is what a reader
  standing at a prompt is actually looking for. It closes the page instead of a link out
  to the docs index: a page about the shell should end with what to type into it. The one
  filter narrows the shelf and the catalogue's rows together, so `git` leaves the git
  commands standing. `/shell` is what the header's Terminal item and the Terminal tile
  swap into the pane while they show and focus the shell: the page about the thing the
  click just took you to. Not to be confused with `/terminal`, which *is* the shell (the
  right pane's own document).

  **The tile is one object across every page** — the strip, docs, topics, and the head of
  every century grid on solutions — and it is **two lines**, because that is what it has to
  say: what it is, and one fact about it.

  | line | what it holds |
  |------|---------------|
  | first | the section's mono glyph (π · § · λ · ❯), the **title** beside it, and the corner slot — arrow / padlock / `final` pill |
  | second | the **supporting line** |

  The glyph sits with the name it marks rather than on a line of its own, so a 16-tile
  grid reads as 16 short blocks and not as a column of floating glyphs. A title too long
  for its track takes a second line (then ellipsis), with the glyph and the corner mark
  staying on the first.

  The supporting line is the rule that makes the pages one system: **mono when it is a
  number, body face when it is a sentence**. The strip, topics and centuries carry a count
  (`95 of 240 solved`, from `topics/articles.json` and `problems.json`); a guide carries
  prose (its `#` title). Nothing carries both — a tile says one thing about itself. Signed
  out the strip has no clone to count, so its tiles fall back to prose rather than to a
  number that would be invented.

  Where the count is a **fraction of work done**, the tile also carries a 2px **progress
  hairline** on its bottom edge, filled to that fraction. It appears on topic tiles and
  century tiles and nowhere else: its absence on a guide says "not a progress thing"
  rather than "zero". The width is the app's one inline `style` — it *is* the datum, and
  there is no class-per-percent worth having (`style-src 'unsafe-inline'` is already a
  recorded exception, below).

  The corner slot holds affordance or state, never decoration. The `→` fades in on
  hover/focus — sixteen resting grey arrows in a grid this dense is noise, and a bordered
  box on a card grid already reads as clickable — while the padlock (signed out), the
  `final` pill and the strip's you-are-here mark are state and stay put.

  Four per row is set for the pane the terminal leaves (half the viewport); below a 1200px
  viewport the grid drops to two and below 700px to one, because under ~150px a tile
  truncates its own title.

  The **Terminal** tile, and the header's Terminal item with it, points at two things at
  once: the shell already here in the right pane, and `/shell`, the page *about* it. So
  each is an ordinary `hx-get` link that also carries `[data-term-show]` — the pane swaps
  to `/shell`, and the terminal is *shown* when it has been hidden to the footer and
  *focused* either way. Show means "take me to the terminal", and a control that reveals
  the shell but leaves the next keystroke going nowhere has done half its job; `site.js`
  does not `preventDefault`, so both halves run on the one click. Focus is the iframe's to
  give (`{euler: 'focus'}` — the parent cannot reach xterm's hidden textarea across the
  boundary). The socket is untouched: connecting is the titlebar's act (§ Header).
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
  the heat tokens, title and pct on hover. Each grid is **headed by the tile**: the range
  where the glyph goes, `36 of 100 solved` on the data line, and the hairline along the
  bottom edge pointing straight into the grid it measures — a century is a topic you have
  or have not worked through, so it says so the same way. It is an `<h2>`, not a link
  (there is no per-century page), so it keeps the chassis and drops the hover.
- **Progress upload** — an **empty** paste buffer, because this is a *replace*, not an
  edit: the previous `.progress.html` is superseded wholesale, parse-or-reject before
  anything lands.
- **Problem** — statement first, then test cases · results · files · notes. Two off-site
  links on the meta line (projecteuler.net and the GitHub solution directory). Test cases
  render as a table, not raw JSON. Files flow horizontally, plain-text links, zero-size
  files hidden, each name coloured by its git status with the status spelled out in the
  hover title.

  **The statement is foreign content, and it assumes a light page.** It is
  projecteuler.net's own markup, cached verbatim, and two things in it are written for
  their white ground. `content.prepare_statement` meets both on the way out — the dark
  ground stays the design, because a bright panel in the middle of the page would be the
  more visible bug.

  *Emphasis colours.* A statement asks for colour three ways, and all three land on
  `content.STATEMENT_COLOURS`: the LaTeX `\color{…}` MathJax renders (the case that
  started this — no stylesheet can reach it, since by the time CSS applies MathJax has
  turned it into a fill), an inline `style="color:…"` (which CSS could only beat by
  shouting `!important`), and their `class="red"` spans (the stylesheet's `.statement
  .red` rules, scoped so a generic `.red` cannot collide). Each maps to the same hue
  lifted for a dark ground: `#3333ff` on `#0f1115` was the reported case. A colour outside
  the table is left exactly as written — the author's own value beats a guess.

  **The TeX form emits `\color[RGB]{r,g,b}`, never a `#` literal**, and that is not a
  style preference. `#` is TeX's macro-parameter character, and `\color` arrives from an
  *autoloaded* extension (§ the vendored TeX extensions above): on the first statement to
  use it, MathJax parses the argument as ordinary math while the extension is still in
  flight, and a `#` there is `You can't use 'macro parameter character #' in math mode` —
  a rendered error, not a retry. A first cut that emitted `\color{#7cc0ff}` shipped this
  and it hid well, because the race only loses one way round: reaching a problem by
  **htmx swap** hit the window and broke, while a **full refresh** had the extension
  cached and rendered perfectly. `\color{blue}` never showed it — `{blue}` is valid math,
  four italic letters — so every colour projecteuler.net actually writes was immune.
  `[RGB]{r,g,b}` is the LaTeX-standard model form (the vendored `color.js` implements
  `rgb`, `RGB`, `gray`, `named` — there is no `HTML` model) and contains nothing math mode
  objects to; it is verified in a headless render both with the extension loaded and with
  it deleted outright.

  *Transparent diagrams.* A see-through image takes the page's ground. Of the cached
  statement images 43 are dark line art on transparency — a black diagram on a near-black
  field, on problems as ordinary as 15, 86 and 91 — while 29 are light ink that our ground
  suits exactly, and 183 are opaque and carry their own background.
  `content.plate_statement_images` reads the pixels (`_image_ink`, Pillow, cached per file
  by mtime and size) and marks only the dark-ink ones `ink-dark`; the stylesheet gives
  those a light plate. **The pixels are the only honest source** — projecteuler's
  `class="dark_img"` sits on 37 of the dark-ink images and 20 of the light-ink ones, so it
  does not tell them apart in our cache. p0091 carries one of each in a single statement,
  which is the whole reason no single background could have worked. Pillow's absence
  degrades to "no plate", which is exactly the old rendering.

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

### 11.9 The git chip

The header's chip (`_git.html`) reports **this collaborator's clone** — branch, divergence
from `origin/master`, worktree counts, and whether the private solutions are readable —
and offers the verbs that move it. Same `<details class="menu">` chassis as Actions and
the user pill: one menu idiom in the header, not three.

**Quiet when clean.** An in-sync branch with nothing uncommitted is a glyph and a name in
`--muted` — no counts, no tick. Every mark that appears is something to act on: ahead in
`--git-staged` (yours, ready to go), behind in the accent ink (the pull you owe), and a
`--git-modified` **ring** for a dirty worktree — a ring, not a disc, so it cannot be read
as the terminal's connect dot two controls to its right.

**One read per navigation.** `solver/web/site/gitstate.py` reads the chip on each
navigation; a middleware in `install_content` stashes it on the request (`render` is sync
and cannot await), and `render._context` picks it up. Three commands, **staged by what each
one needs**, so a partial failure costs only the part that failed:

1. `git rev-parse --abbrev-ref HEAD` — the branch. A pure ref read: no worktree scan, no
   filter, works with the vault locked. The spine; if even this fails the clone is
   genuinely unreadable (`unknown`, "state not read").
2. `git rev-list --left-right --count origin/master...HEAD` — the divergence. Also refs
   only, no filter.
3. `git status --porcelain=v2` — the worktree file counts. The one read that scans files.

**Always `origin/master`.** Not the branch's tracking branch, and so *not* `git status`'s
own `# branch.ab` — that field counts against `origin/user/<slug>` and answers "have I
pushed?". The question this workspace turns on is "how far am I from **master**?", because
master is where work lands and `git-sync` closes the gap. The chip measures what
`scripts/git/status.sh` measures, against the same ref; the two must not drift.

**The worktree read needs the vault; branch and divergence do not.** With the filter wired,
`git status` hashes `solutions/private/**` through the clean filter, which needs the master
key, which needs the vault unlocked. Right after login the vault is still locked — the
browser posts `/vault/unlock` only *after* the first render — so this read fails on the
first paint. Because it is staged last and on its own, the chip is then `worktree_unknown`,
**not** blanked: branch and divergence show, the panel says "worktree state pending — unlock
the vault", and a hollow dot (not the amber dirty ring) marks it, because three zero counts
we could not read must never render as "clean". `site.js`'s auto-unlock fires
`euler:git-changed` the moment it lands, so the worktree fills in a beat later without a
navigation. (Before this staging the whole chip read "state not read" on every first load —
and its cause was invisible, because the read discarded git's stderr; it now logs it, since
128 alone names none of a locked vault, a dead filter, or a missing ref.)

**Freshness against the remote — fetch where it is worth blocking, not on every swap.** The
divergence answers "how far am I from origin/master?", and the honest answer is against the
remote *as it is now*: a clone that never fetches reads "level" while the remote moved ahead
(the bug that surfaced this). So `gitstate.read` takes `fetch`, and runs a `git fetch origin
master` — like `status.sh` — before the count when it is set. A fetch is a network round
trip that blocks the render it runs on, so the caller spends it only where the user expects
freshness and not on every pane swap:

- **full page loads** (login, reload — `not HX-Request`) and the **chip's own `/git`
  endpoint** (its `git-changed` refresh and the 10-minute poll) → `fetch=True`;
- **content navigations** → the local ref, never blocking on the network.

`git-sync` fetches on its own, so after one the ref is already current. Every fetch is
throttled on `.git/FETCH_HEAD`'s mtime (which any fetch resets, `git-sync` included), so
rapid reloads — and a load right after a sync — do not re-hit the remote; a slow or offline
remote falls back to the local ref within a short timeout rather than hanging the load.

**The chip refreshes itself, and swaps its CONTENTS to do it.** `_git.html` is the
element — the `<details>`, its triggers, and the `.term-offline` class `site.js` paints on
it; `_git_menu.html` is what `/git` returns and what lands inside it (`hx-swap="innerHTML"`,
and `hx-swap-oob="innerHTML"` for the per-navigation swap). The element has to survive its
own refresh, because it holds the open state — this is the shape the message chip settled on
first (§13), and the git chip joined it when the second trigger below arrived. Consequence
worth knowing when editing: **every state class the chip wears rides on the `<summary>`**,
not on the `<details>`, since an inner swap cannot reach the outer element's attributes.

Three triggers, no overlap:

- **`euler:git-changed from:body`** — the shell moved the clone. Git commands run in the
  *terminal*, which is not a navigation, so `solver/core/osc.py` says so over OSC 5379 and
  `site.js` turns it into the event (the vault's auto-unlock fires it too, to fill in a
  worktree the first paint could not scan).
- **`toggle[this.open] throttle:1s`** — the user opened the menu. The push above can be
  missed: it rides the terminal's WebSocket, so a disconnected or hidden terminal drops it
  silently, and an external push moves `origin/master` with nothing local to notice. Opening
  the menu is the one moment a person is *asking* where their clone stands, and it is
  exactly when the answer must not be whatever the last navigation happened to read. The
  filter keeps it to *opening* — a bare `toggle` fires on close too, spending a read on a
  panel nobody is looking at any more.
- **`every 600s`** — the slow poll, so an external push shows without the user reloading or
  running a git command. `/git` reads with `fetch=True`, so this is the one that goes to the
  remote on its own. It used to be a separate `<span class="git-poll">` in the header,
  because an oob `outerHTML` swap on every navigation restarted an `every` timer placed on
  the chip; with the contents swapping instead, the element survives and the timer lives
  where it belongs — and no longer fires on a tier that has no clone and no `/git` to answer
  it.

**Two inert states, and they are not the same.** No clone at all (`git is None` — the auth
tier, or a uid without access to `.git`) renders a plain span: no id, no triggers, nothing
targets it, and nothing ever will within that document. A clone that is *there* but would
not answer (`unknown`) renders the **real** chip, wearing an absent branch name and saying
"branch state could not be read" — it keeps the verbs, because `git-status --details` in the
terminal is exactly the diagnosis the chip cannot make for itself, and it keeps the triggers,
because an unlocked vault a moment later resolves it. The "private solutions" row is dropped
there: that state never reached the read that sets `filter_wired`, and reporting "locked"
would be a guess dressed as a fact.

**`--no-optional-locks`.** `git status` normally takes `.git/index.lock` to write back its
refreshed stat cache. The chip is a *reader on a page render*, and the user is typing real
git commands into their terminal one pane away: a status read that grabs the index lock can
make their `git-commit` fail. This is git's own answer for status displays — a little
repeated hashing, no lock.

**The verbs type into the terminal.** Each is a `[data-term-cmd]` button (`site.js` → the
`/terminal` iframe), exactly like the account page's tool rows: the web shell is the front
door, so there is one execution path and one audit trail. Hence every verb *names the
command it types* — the menu is a way into the shell, not around it. The floors come free:
the command lands in a shell that already resolved this subject, and `requires()` there is
the boundary whatever the menu shows. `git-commit` needs no problem argument, because the
shell supplies the one it is on, and no message either — the command asks for one at the
prompt, so the row *starts* the commit rather than completing it.

**The rows name the work, not the commands.** "Save my work", not "Commit"; "Land a pull
request", not "Pull requests"; "Un-commit, keep my changes", not "Reset to master". The
command is on every row regardless — the macro renders it into `.cmd` beside the label — so
the menu still teaches exactly what it types, which frees the label to say which of the
day's jobs this is. A panel whose labels are the command names is a transcript of the shell
rather than a way into it, and `git-commit solution docs topics` is a fine thing to run and
a poor thing to call a button. They are ordered as the job runs: see what changed, take what
others landed, save it, hand it over, land someone else's.

**One commit row, three targets.** `git-commit solution docs topics` is a single button for
"save what I did", whichever of those the afternoon went into. Naming three targets costs
nothing when only one has changed: a clean target contributes no path and the commit says
so, which is exactly what makes one row viable where two previously asked the reader to
decide which half of their own work they were saving. `solutions` and `update` are
deliberately not on it — staging the whole tree, or regenerated package source, is not a
one-click act.

**One merge row, because there is one queue.** The panel carries a single `gh-merge merge`
(`maintainer`), which offers the open requests as a menu — so the row needs no number and a
maintainer sees everything that is waiting. It used to carry a second `gh-merge-docs`
button, because the two gates were disjoint and half the queue had no button otherwise;
with one allowlist there is one queue and one row.

**The message chip's merge row names its own request.** A `PR_REVIEW_SUBJECT` notice is
about *one* branch, so `msg act` on it resolves that branch to its request number
(`solver.core.git.merge_pr_for_branch`) and lands it. Offering the whole queue as a menu
there would ask the reader to pick out a request they had just been told the answer to —
and let them pick a different one. The branch in the subject is therefore load-bearing in
both directions: it names the request to merge, and it dismisses the notice afterwards.

**A disconnected terminal is a designed state.** `terminal.js`'s `send()` drops the frame
on a closed socket, so a click would silently do nothing — the one outcome a control must
never have. `site.js` paints `.git-offline` from the same single `termConnected` every
other `[data-term-*]` control reads; the panel then says so and offers Connect.

**Locked private solutions point at Account, not at a self-service unlock.** The private
row reports `decrypted`/`locked` (`gitstate.filter_wired`), but when locked it offers *no*
`git-filter install` verb: the common locked cause is a reader **not yet granted enc-key
access**, for whom install just errors ("gain key access before installing") — they need an
admin to authorise their key first, and the chip cannot cheaply tell that apart from a key
that merely has not been wired. So the row links to `/account`, where the state *is* known
(`can_decrypt`, an X25519 unwrap too costly per-navigation) and the right action is offered:
the public-key panel gives **Create identity** (`user`) when there is no keypair, and **Copy
+ Sync** when there is a key that cannot decrypt yet — `user` has already filed the
request with staff (§13), so this is the follow-up: `git-sync` pulls the grant once a
maintainer runs `user-authorize`, and auto-wires the filter. `git-sync` is
the one command that advances every case and never errors, so it is what every locked path
(the account tool row included) runs; the manual `git-filter install` stays a shell command
for the rare has-access-but-unwired case, unsurfaced where it would mislead.

**The refresh: the shell says when it moved.** A git command runs in the terminal, which is
*not* a navigation — so without a nudge the chip would be most wrong exactly after the user
acted. The git commands emit `OSC 5379` `git;<token>` on their success paths
(`solver/core/osc.py`, the one definition of that wire); `terminal.js` posts
`{euler: 'git-changed'}`; `site.js` dispatches `euler:git-changed` on `<body>`; the chip's
own `hx-get="/git"` (`hx-trigger="… from:body"`, `hx-swap="outerHTML"`) replaces itself.
One read, at the one moment the state changed. It fires for a **hand-typed** `git-sync`
exactly as for the menu's item — the menu types the same command, so there is one path —
and for the sync a web shell runs at startup (§12.1), which dispatches that same command:
the nudge rides `sys.stdout` directly, so the quiet that hides the sync never hides it.
A lost or replayed sequence costs a stale chip until the next navigation, never a wrong one.

**Three states that are not "clean".** With no readable `.git` — the shared content tier
runs as a uid with no access to it — `read()` returns `None` and the chip is inert
("no clone"); that is also what the auth tier's pages render, since they build their own
contexts and never set `git`. When even the branch will not read — the clone is there but
git answers nothing — the chip is `unknown` ("state not read"). And when the branch and
divergence read but the worktree scan is blocked (the locked-vault case above), it is
`worktree_unknown`: most of the answer, honestly labelled pending. None of the three ever
paints "clean" over data it could not read.

### 11.10 Caching

The failure this policy exists to prevent is a response that says **nothing**. With no
`Cache-Control`, a browser may apply *heuristic freshness* — reuse a response for a
fraction of its age since `Last-Modified` — so a file last touched months ago can be
served from cache for days without a single request reaching us. It is invisible from the
server, it only bites the users who happen to hold the old copy, and its symptom is the
worst kind of bug report: "works for me, they need a hard refresh".

Every response therefore carries a directive, stamped by an app middleware
(`solver/web/cache.py`, shared by every service — the same shape as the CSP one above)
and by the edge for what Caddy serves itself. Two classes, split on what the response
**is**, not on what it contains:

| class | directive | why |
| --- | --- | --- |
| rendered pages, htmx fragments, JSON | `no-store` | per-user, authenticated, and stale the moment the file behind it changes; there is no version worth keeping, and it stays off disk on shared machines |
| `FileResponse` — served files, `/assets`, `/vendor` | `no-cache` | identical bytes for every user, already carrying `ETag`/`Last-Modified`: keep it, but **revalidate before every use** — an unchanged file costs one 304, a changed one is picked up at once |

`no-cache` is not "do not cache" (that is `no-store`); it is "ask first". That distinction
is the whole design: the file classes stay cheap without ever being able to go stale.

Two paths need naming because they are easy to miss:

- **Error responses.** A raised `HTTPException` *is* a response, and an unstamped 404 is
  heuristically cacheable like any other — a browser that cached "404" for a problem you
  have since written would keep serving it. The middleware stamps the exception path too.
- **htmx's own history.** htmx snapshots the swapped pane into `localStorage` and restores
  it on Back **without asking the server** — a cache no HTTP header reaches. Since this
  app's content changes underneath the browser (you edit in the terminal, or another tab),
  `base.html` sets `<meta name="htmx-config" content='{"historyCacheSize": 0}'>`: Back is
  a history miss, and htmx re-requests the pane (`refreshOnHistoryMiss` stays `false`, so
  it is an ajax fetch, not a full reload).

**No positive `max-age` anywhere, deliberately.** Nothing here is addressed by a versioned
URL: `/assets/site.css` is the same path before and after a redeploy. Caching those hard
would need content-stamped URLs (`site.css?v=<hash>`) generated into the templates and an
edge rule marking versioned requests `immutable` — a real option if revalidation traffic
ever matters, but until then "ask every time" is the honest setting, and one conditional
request per asset is a rounding error against a page that also fetches MathJax.

## 12 · The web shell

The terminal is the front door: **every rung gets one**. What varies by rung is what the
shell *inside* it will run, not whether it exists. It is the full `solver` shell — lexer,
parser, interpreter, prompt-toolkit — not a curated command protocol, because reusing the
hardest proven code with authorization already enforced at registration beats inventing a
bespoke command surface.

Attach is gated on the `reader` floor plus a live session plus a one-time ticket. Inside,
the rungs diverge by the same decorator floors as everywhere else (§6.6): a `reader`
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

**A web shell syncs its clone as it starts.** `run_interactive` dispatches `git-sync`
before the first prompt, on the **web channel only** (`config.subject.channel`) — a
terminal user drives their own clone and did not ask for a fetch. Without it a
collaborator opened onto whatever their clone held when they last used it, and the
enc-key pull flow (§9) that wires their filter waited on them remembering to type the
command. It runs with the shared console quiet, which also routes the sync script's own
output to `DEVNULL` (`run_cmdline`), so the banner is followed by a prompt rather than a
wall of git; a **failed** sync still prints one line, because a stale clone with no hint
is the one outcome silence must not cover. An interrupt during the fetch is absorbed by
the register adapter, so a Ctrl-C at startup still lands at a prompt.

Note what "at startup" means against the persistence above: this is once per **shell**,
not once per attach. Re-opening the tab re-attaches to the running shell and syncs
nothing — the fresh fetch comes with a new shell, i.e. after a teardown or the 24 h
detached reaper. The chip's own remote-fetch freshness (§11.9) is what keeps a
long-running shell's *view* current in between.

### 12.2 Four client-side subtleties

**The shell is the front door for interactive logins.** The account page's tool rows
(GitHub CLI, Claude Code) make the *status* the button: clicking posts
`{euler: 'run', command}` to the iframe, which types the command and a return into the
PTY — `git-identity` and `! claude /login` respectively. Nothing there is privileged: it
is the same PTY the keyboard writes to, the command is echoed, and it is the user's to
edit or interrupt. These logins are interactive device flows that belong in a terminal,
and a web form that "did it for you" would have to handle a credential it has no business
touching. With no session attached there is nothing to type into, so the iframe says so in
the terminal rather than dropping the click silently.

Because those commands run in the terminal and not through a navigation, the panel they
change would otherwise go stale — so they nudge it the way a git command nudges the chip.
`user` (a new identity) and `git-identity` (a GitHub sign-in) emit `OSC 5379` `account;`,
which `site.js` turns into an `euler:account-changed` body event; `#vault-panel` carries
`hx-trigger="… euler:account-changed from:body, euler:git-changed from:body"` and refetches
`/account/vault`. The git event is on the list because `git-sync` / `git-filter` change
decrypt access too — so those emit only `git;` and the panel picks it up, rather than any
command emitting both. The refresh is **scoped by presence**: `#vault-panel` is in the DOM
only while `/account` is the visible pane, so the body events reach a listener — and cost a
fetch — only then, and are inert otherwise. `! claude /login` is a bash passthrough and
cannot emit the nudge itself, so its row chains `&& git-sync`: the shell's `&&` runs the
nudging command the instant the interactive login succeeds (and skips it if the login is
cancelled), and `git-sync`'s `git;` refresh reaches the panel too. It is safe to chain —
`git-sync` stashes a dirty tree and rolls back on failure, never leaving a half-synced repo.

Reporting on those tools means finding them the way the *shell* does: the service's PATH
is systemd's, not a login PATH, so `vault_api._which` also looks in `~/.local/bin` — where
per-user installs land (`claude` does). A tool the user can run in their web shell must
not read as `not installed` on their account page.

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

**Enter carries its modifiers — when the application asked for them.** xterm.js sends Enter
as a bare CR whatever else is held down (its keyboard knows only Alt, as ESC CR), so
Shift-Enter used to reach the PTY indistinguishable from Enter, and the tools that read that
chord as "newline, don't submit" — Claude Code — never saw it. Two encodings carry the
modifier, kitty's `CSI 13 ; <mod> u` and xterm's modifyOtherKeys `CSI 27 ; <mod> ; 13 ~`, and
**neither may be sent unasked**: a reader that knows only the legacy encoding takes the second
for text and lands `;2;13~` in its line buffer, which is precisely what bash does. So
`terminal.js` watches the enabling sequences go past on the way out (`CSI > <flags> u` /
`CSI < u`, `CSI > 4 ; <n> m` / `CSI > 4 m`) and encodes to match whatever the foreground app
turned on. With nothing on — the common case, since Claude Code *requests* those protocols
only for terminals on its own allowlist, which this one is not — it falls back to what a
terminal user would have bound by hand: ESC CR for Shift and Alt, which is Meta-Enter to any
readline-ish reader and the newline Claude Code's `/terminal-setup` installs for this key in
editors' terminals, and LF for Ctrl. The fallback costs the solver's own prompt nothing:
prompt-toolkit accepts the line on all three, exactly as it did on a bare CR.

Modes, unlike the OSC actions above, *are* rebuilt from the replay. An action must not
re-fire; a mode is the state of the shell being reattached to, still running whatever app set
it — and since the buffer drops its oldest bytes, an enable can only be lost before, or along
with, its disable, never after. The kitty **query** (`CSI ? u`) is deliberately left
unanswered: this client encodes Enter and nothing else, so advertising a flag set would
promise an app the disambiguated Esc and Tab it would then sit waiting for.

## 13 · Messaging

**Every message stands on its own — there are no replies.** The spool is not an email or
chat replacement: it is how a *command* tells somebody something they must act on, and the
act is always on one message. A request and the grant that answers it are two messages with
two verbs, which is precisely what lets the header chip name the verb a row is for. Threading
bought conversation nobody was having, and cost a second place for content to hide — an
answer buried in a reply is invisible to anything reading the message it answers, which is
exactly how taking a key came to look in the wrong place for one.

**This is a mechanism for commands, not a chat feature.** Its purpose is to let a command
tell staff something they have to act on. The founding case is `user`: it mints a keypair,
and the public key is inert until a maintainer runs `user-authorize` on it — so the command
files that request itself, where before the account page said *"copy your public key to the
admin and wait"* with nothing behind the waiting.

Everything below follows from that framing, and reading it the other way — as an inbox
people write in — is what makes this tier look bigger than it is.

Three flows, and only three:

- any user (or a command running as them) → **staff** (`maintainer`+);
- staff → **one or more named users**;
- staff → **everyone** (a broadcast notice).

There is no user↔user leg. **Every message has staff at one end**, so there is no presence,
no peer graph, no per-pair ACLs and no cross-peer ordering to get right. Widening it to
peer-to-peer later is a redesign, not a setting.

Delivery is **asynchronous by construction**: the spool is the system of record and the
recipient reads when they next look. A message is never lost because someone was offline,
and nothing in the path waits on a live connection.

**Reading and writing happen in the shell.** The web surface is one header chip and
nothing else — no page, no thread view, no compose form. That is not an omission to fill
in later: the browser holds **no write route to the spool at all**, so every message and
every message arrives over `msg.sock` from a uid the kernel vouched for, and the command's
own `requires()` is the only gate there is. A guarded write surface would be strictly more
to get wrong than an absent one.

### 13.1 Why its own service

The spool holds attacker-authored free text — by design, that is what a message *is*. The
auth service was the obvious host (it is the only service every collaborator can already
reach), and it was rejected: it holds the SRP verifier database, the session table and the
ticket mint, so a parsing or authorization slip in a message path would land in the one
process whose compromise is total. That is the same reasoning that keeps the Gmail
credentials in `euler-smtp` rather than in auth (§3) — **a secret lives only with the
service that performs its operation**, and the converse holds too: an untrusted-input
surface lives *away* from the secrets it has no business near.

Two cheaper designs were also rejected, and for reasons worth keeping:

- **A shared spool directory with drop-box permissions** (`0730`, group-owned, senders
  `O_EXCL`-create, `st_uid` attributes the sender unforgeably). Elegant, and needs no new
  service at all — but restricting "only staff may write to a user's box" requires a unix
  group shadowing the profile ladder, reintroducing exactly the per-path filesystem-ACL
  layer the per-user model retired (§6.1). Worse, a demoted maintainer would keep
  broadcast rights until their group membership was fixed, breaking the immediate-revocation
  contract of §6.4.
- **Per-user mailboxes in each collaborator's own tree**, pushed to their instance. Good
  at-rest story, but offline recipients, deprovisioned instances and retries all need a
  central spool anyway — and the operator is an os-login `admin` with no instance at all,
  so the staff inbox would have nowhere to live.

So: a dedicated `euler-msg`, and the isolation is real rather than nominal because of one
observation — **`system_slug()` is a pure SHA-1 of the normalised e-mail**
(`solver/auth/identity.py`), and `authorizations.json` is world-readable. The service can
therefore build its own `slug → e-mail → profile` map from the policy file every other
service already reads. It follows that `euler-msg`:

- is **never routed by Caddy** — the per-user instance is its only web-facing consumer, and
  `/messages` already routes there through `forward_auth` like any other content path, so
  the edge needs no new rule;
- **never talks to the auth service** — no cookie forwarding, no shared secret, no ordering
  dependency between the two units;
- runs **`RestrictAddressFamilies=AF_UNIX`** — it cannot open a socket to anything, ever,
  which is strictly harder than auth (which needs `AF_INET` for the mail relay).

Its blast radius is message bodies and read-state. Nothing else is in the process.

The package is a sibling of the other service packages, and imports **nothing** from
`solver.web.auth` — loading auth's modules into this process would recouple the two at
review time and defeat the point:

| Module | Role |
|---|---|
| `__main__.py` | Entry point: bind `msg.sock` (`0660 euler-web`) + `msg-admin.sock` (`0600`), serve until SIGTERM. |
| `config.py` | `MsgConfig` from the environment — variable names and defaults in `[msg]` of `solver/config/env.conf`; every path overridable for a scratch-dir dev run. |
| `app.py` | The public and admin apps: endpoints, the peer-uid middleware, profile floors, the delivery push. |
| `store.py` | The thread store — single-writer JSON, TTL sweep, caps, read-state. |
| `identity.py` | Peer uid → login → e-mail → profile, over `authorizations.json`; re-read on mtime change. |
| `admin.py` | The sudo-gated proxy behind the operator's terminal path (§13.3). |
| `commands.py` | The `msg` shell command (§13.7). |
| `notify.py` | `notify_staff()` — how a *command* sends, and the reason the tier exists. |

Three utilities move up out of the auth package so both services can use them without
either importing the other:

| Was | Now | Why it is shared |
|---|---|---|
| `auth/client.py` | `solver/web/unixhttp.py` | the unix-socket JSON client, wanted by both admin CLIs |
| `auth/storage.py` + `requests.py::sanitize` | `solver/web/store.py` | atomic `0600` JSON writes, and control-char hygiene for the two stores that hold user-authored text |
| `auth/admin.py::_env_file_values` | `solver/web/envfile.py` | reading a scoped `/etc/euler/*.env` for a root-only admin token |

`auth/client.py` and `auth/storage.py` remain as re-exports, so nothing downstream changes.

### 13.2 Identity and authorization

**The kernel is the identity.** Every request on `msg.sock` is authenticated by
`SO_PEERCRED` — the same mechanism the per-user unit already calls authoritative (§7). The
peer uid *is* the slug; the slug resolves to an e-mail through the `system_slug` reverse
map; the e-mail resolves to a profile through `authorizations.json`. There is no `from`
field on the wire, so there is nothing to forge, and no bearer token on the hot path to
leak. The per-user service and its PTY children share a uid, which is correct — they are
one principal.

Authorization is the same rank comparison as everywhere else, resolved **per request**
against the policy file, so a demote lands within one request rather than at next login:

| Verb | Floor |
|---|---|
| read own inbox, mark read | `reader` |
| send to staff | `reader` |
| read the inbound queue, send notices | `maintainer` |
| notice to named users, notice to everyone | `maintainer` |

The `reader` floor on *sending* is deliberate: a new invitee's first need is often to ask
a question, and the terminal is the front door for every rung (§12).

### 13.3 The wire contract

```
GET  /messages?since=<iso>      this slug's threads + unread count      reader
POST /messages                  {subject, body} → the staff queue       reader
POST /messages/<id>/reply       {body}                                  reader (own thread)
POST /messages/<id>/read        mark read                               reader
GET  /staff/queue               the inbound queue                       maintainer
POST /staff/notice              {to: [email…] | '*', subject, body}     maintainer
```

The **admin socket** (`/run/euler-msg/admin.sock`, `0600`, euler-msg-private) carries the
same staff verbs for the operator's *terminal*, reached under `sudo` with a token from
root-readable `msg.env` — exactly the wheel-gated shape of the auth admin plane (§6.5), and
for the same reason: the operator's ordinary uid is the most exposed on the host and is
deliberately **not** in `euler-web`, so it cannot dial `msg.sock` at all.

It lives in the service's **own** runtime directory (systemd `RuntimeDirectory=euler-msg`,
`0700 euler-msg`) rather than in `/run/euler-adm`, which is `0750 euler-auth` and so not
writable here. Each admin plane owning its own directory is the better shape anyway: root
traverses either, and nothing else traverses both.

The CLI behind it (`solver/web/msg/admin.py`) is a **thin authenticated proxy**, not a
second command surface — it takes a method and an admin path, injects the invoking
identity, and prints the reply as one JSON line, so a single renderer serves both channels
and the terminal cannot drift from the web. Two details there are deliberate: the request
body arrives on **stdin**, never in `argv` (a message body in the process table is readable
by every uid on the host through `/proc`), and the identity is `SUDO_USER` rather than an
argument — root could assert anything, but a typo cannot file a message under a stranger's
name, and the profile check still runs against the policy file.

### 13.4 State

`/var/lib/euler-msg`, `euler-msg`-only `0700`, single-writer (one process). One record per
**thread**, not per recipient:

```json
{ "id": "…", "kind": "inbound|notice", "author": "<slug>",
  "subject": "…", "body": "…",
  "recipients": {"<slug>": {"read": "iso|null"}},
  "replies": [{"author": "<slug>", "body": "…", "at": "iso"}],
  "created": "iso", "updated": "iso", "expiry": 0 }
```

A broadcast is therefore **one record with N recipients**, not N copies: "everyone" is
cheap, read-state stays per-person, and a collaborator provisioned after a notice was sent
is simply not in it — which is the correct behaviour, not an omission.

Bodies are **plaintext only**, `sanitize()`d on the way in (control characters stripped,
length-capped) and rendered through Jinja autoescape. No markdown, no HTML, no rich
rendering. That *deletes* the injection class rather than defending against it, which
matters more here than anywhere else in the stack precisely because this store exists to
hold text other people wrote.

Bounded like the invite queue it resembles (§4.6's neighbour, `requests.json`): a per-sender
standing cap, a global cap, and a TTL swept on every access, so an unworked queue cannot
grow without limit.

### 13.5 Delivery

Five ways the count reaches you, all reusing machinery that already exists:

1. **Live nudge.** `euler-msg` POSTs `/internal/message` to the recipient's own
   `user-<slug>.sock` — the same socket-peer-only push the auth service uses for logout and
   vault-reset teardown (§12.1); `euler-msg` carries `SupplementaryGroups=euler-web` to
   reach it. The instance sends a `{"euler":"message","unread":n}` **TEXT frame** to any
   attached browser terminal, which relays it to the page as an `euler:message` body event.
   A recipient with no terminal open notifies nobody, and that is not a failure — the count
   is waiting for them at (2).
2. **On document load.** The chip fetches `/messages` on `load`, so a full page load is
   always current whether or not a push ever reached the user. It is deliberately **not**
   sent out-of-band with every pane navigation the way the git chip is: the count moves when
   someone *else* acts, which no navigation can predict, so a spool read per navigation would
   buy nothing. The push is only a nudge — a lost one costs a stale count until the next
   document load, never a lost message.
3. **On opening the panel** — `hx-trigger="toggle[this.open] throttle:1s"`. (1) and (2) are
   both pushes, and a push can be missed: the live nudge rides the terminal's WebSocket, so a
   disconnected or hidden terminal silently drops it, and `load` has not fired since the last
   full document load. Opening the menu is the one moment a person is *asking* what is
   waiting, and it is exactly when the answer must not be twenty minutes old. The filter is
   what keeps it to opening — a bare `toggle` fires on close too, spending a fetch on a panel
   nobody is looking at any more; htmx calls a trigger filter with the element as `this`
   (`eventFilter.call(elt, evt)`), so `this.open` reads the state the event just produced. The
   throttle is because the trigger is a pointer away from being held down: it fires the first
   open and drops the rest of the second, which no reader can perceive as staleness.
3. **The shell's own nudge.** The three above cover a message *arriving*. Reading one is
   the user's own act in their own shell, which no service sees — so the `msg` command
   emits **`OSC 5379` `msg;<token>`** on every path that changes what the chip shows
   (`read`, `send`, `reply`, `notice`, `dismiss`), exactly as `git-sync` does for the git
   chip. `terminal.js` turns it into the *same* `euler:message` body event the delivery
   frame produces, so the chip has one listener and does not care which side moved.
   Read-only verbs (`list`, `queue`) emit nothing: a nudge that fires when nothing changed
   trains the reader to ignore it.

   Without this the chip is at its most wrong exactly after the user acted — they read the
   one unread thread and the badge still says 1 until the next full page load.
4. **In the terminal.** `msg list` is a `reader`-floor command, so the count is always one
   command away regardless of what the browser chrome is showing.

**The chip** is a `<details class="menu">` on the same chassis as Actions, the git chip and
the user pill — one menu idiom in the header, not four. It carries the state in two counts
(`N unread, M threads`, shown even at zero), then up to five threads newest-first with
unread ahead of read, then the verbs. Every row and every verb is a `data-term-cmd` button:
a row types `msg act <id>`, and the shell does what that message asks and prints the result
there. So the body never reaches the browser at all, and the boundary is the command's own
floor rather than anything this menu decides to show. When the terminal is disconnected the
panel says so and offers to connect it, painted from the same `termConnected` every other
`[data-term-*]` control reads — a verb that silently does nothing is the one outcome a
control must never have.

**Every row types the same command and says what it will do.** One entry point, `msg act
<id>`, because a message knows what it is for — the rows used to type four different commands,
which meant `msg_api.py` decided what a row was for and the command decided again. Now
`verb_for` (§13.7) decides once, and the row renders only its **label**:

| the row is | the label it carries | what `msg act <id>` does |
| --- | --- | --- |
| a **key issued to you** | save | writes your enc-key file, reading the payload from the thread over the socket, so no key material reaches the browser |
| **half a key** (`key-split`) | reconstruct | `key-reconstruct <share>` — the sealed half is read from the thread over the socket, unwrapped with your private key and completed with the half committed in your clone; same destination as save, one step longer |
| somebody else's **key request**, read by staff | authorize | `user-authorize <id>` — the public key is read over the socket, and nobody retypes 64 hex characters off a screen |
| a **pull request**, read by staff | merge | `gh-merge merge` — no id is needed, the verb walks the pull requests as GitHub knows them, and the merge closes this notice by the branch in its subject |
| anything else | *(none)* | prints it and marks it read |

The label appears only when the act is not a plain read: a row that says "save" or "merge" is
telling you something, where "read" on every line is noise. A rung below staff gets no label
on a key request or a pull request, because for them acting on it *is* a read — `verb_for`
applies the ladder once rather than the chip spelling it out again. This is also why a
request and its answer being two messages matters: one message, one act.

That the ladder shows on a *row* by omission, not by a locked button, is a deliberate
exception to this panel's shown-but-locked rule. A locked verb in the verb list teaches the
ladder on a menu everyone sees; a locked one on a row would ride on every message of a kind
most readers never receive, and on a reader's own key request it would offer them a grant
they can never make.

The panel's two verbs are `msg list` and `msg send`, both `reader`. It used to carry `msg
queue` (`maintainer`) as well — a second name for the part of `msg list` staff already see.

That mechanism is selected by the **`.term-menu`** marker every such menu carries, not by
each menu's own class. It used to be `.git-menu`/`.git-offline`, which meant the second
menu to need it could not join without editing `site.js`.

**The two nudges use different transports on purpose.** A *service*-originated push must
not use `OSC 5379`: that channel rides the PTY byte stream and is replayed into a
reattaching terminal (§12.2), so it would re-fire on every page load and would need the
monotonic-token dance to be safe. A TEXT frame is out-of-band, is never replayed, and needs
no token. A *shell*-originated nudge is the opposite case — it is already on the shell's
stdout, the replay guard already covers it, and routing it out to the spool and back would
invent a second mechanism for something the terminal already carries. So the rule stays
exactly as it reads: OSC for what the shell did, TEXT frames for what the service did.

### 13.6 No mail

`euler-msg` sends no e-mail, which is what lets it stay `AF_UNIX`-only. The consequence is
stated plainly: **a user→staff message waits for staff to open a shell or a page.** For an
invited set of collaborators with a host the operator works on daily, that is an acceptable
latency, and the spool never drops the message.

Adding a digest nudge later is a deliberate, separate decision with a real cost — it needs
`AF_INET` in the unit, an entry in the mail relay's permitted-sender list in
`firewall.sh`, and it gives up the "cannot open a socket" property above. Do not add it as
a convenience.

### 13.7 The `msg` command

Verb-split like `users` (§6.5), registered from `solver/web/msg/commands.py`. Whichever
plane answers is `client.py`'s problem: a web shell's uid is in `euler-web`, so the PTY
child dials `msg.sock` directly; the operator's terminal uid deliberately is not, and falls
back to `sudo` against the admin socket.

```bash
msg list                                       # everything waiting for you, newest first
msg read <id>                                  # one message, and mark it read
msg act <id>                                   # do what it asks (see below)
msg send subject="…" body="…"                  # → staff, the default audience
msg send to=u3f9a2c,u81b0de subject="…" body="…"           # STAFF-only recipients
msg send to=everyone subject="…" body="…"      # STAFF: broadcast
msg dismiss <id>                               # drop a message you are done with
```

Recipients are named by **slug**, and the menu offers them from the roster (§6.3) — a plain
file read, so a maintainer over the web gets the same list the operator's terminal does. An e-mail address still resolves (`box_of` collapses either form to the same
box key), but nothing has to publish one to address a message.

The subject and body are `name=value` tokens rather than bare positionals because the
message id is the one argument that reads naturally in the leading position — `msg read
<id>` and `msg act <id>` are the two forms typed most often.

**Five verbs, one per thing a person does with a message.** There were seven. `queue` was
`list` with a staff-only filter over a mailbox that already shows staff every inbound
thread, and `notice` was `send` with a different `to` — both marked STAFF in the menu, and
both refusing *after* walking a `contributor` through subject, body and recipients. A menu
that offers what it will then refuse teaches the ladder in the worst possible place. The
ladder now lives in what a verb **asks**: `to` is only asked of staff, because below that
floor there is one possible answer (`staff`), and it is the default.

**`act` is the message's own verb.** `save` used to be a verb for one message kind, so the
reader had to know which of seven verbs their message wanted. A message knows what it is
for: `verb_for(subject, is_staff=…, is_own=…)` in `solver/web/msg/__init__.py` maps it to
**save** (take the key it carries), **reconstruct** (complete the *half* key it carries with
the half committed in the clone — `key-split`'s message), **authorize** (grant the key it asks
for — staff, and not your own request), **merge** (land the pull request it announces —
staff), or **read**.
That one function is also what labels the header chip's rows, so the button and the command
cannot drift, and the two staff acts are unreachable below `maintainer` because the function
never hands them out there. Each act cleans up after itself, so nothing is left to dismiss:
taking a key drops the message that carried it, granting one drops the request, and a merge
drops the notice (§13.7 above).

**`dismiss` is not floored in the command.** The service already answers that question
better — staff may drop anything, anyone else a message they are a party to — and the old
`maintainer` check meant the rung that most needs the tidying, a reader clearing a worked
notice, was the one refused.

**Commands send through `notify_staff`** (`solver/web/msg/notify.py`), not through the
command layer:

```python
from solver.web.msg.notify import notify_staff
notify_staff(subject, body)      # -> bool, best-effort, never raises
```

Two properties every caller depends on. It is **best-effort**: a wedged or undeployed spool
must not fail the act that was trying to report itself — `user` still mints the keypair, and
the operator learns of it the next time they look. And it **prints nothing**: these fire
inside another command's flow, which owns what the user reads, so a failure is logged rather
than dropped into the middle of someone's key output. It is stdlib-only, so a command can
call it in a base install with no aiohttp.

`user` is the first caller, and only on the path that needs it — a key was **just minted**
*and* it cannot decrypt, so somebody with the master key has to act. A key that already
decrypts needs nothing, and a bare `user` status view is not a request.

Two more callers, on the same terms — the act is the system of record, the message is a nudge
on top, and each subject is a constant in `solver/web/msg/__init__.py` so the chip can offer
the right verb:

- **`git-push`**, when it opens a pull request (`PR_REVIEW_SUBJECT`): a pushed branch with a
  request nobody has been told about is the same dead end `user` had before this layer
  existed — the collaborator has done all they can, and the act that lands it belongs to
  someone with no reason to be looking. Only for a *newly opened* request: re-pushing a branch
  as it grows keeps the one open request, and a notice per push would turn the queue into a
  changelog of somebody's afternoon. The reviewer's verb is `gh-merge merge`.

  **This one closes itself.** `gh-merge` dismisses the notice for each branch it lands
  (`_dismiss_pr_notice` → `notify.dismiss_by_subject`), so a worked review does not leave its
  own instruction in the queue — the same tidying `msg act` does for a taken key. The handle
  is the **subject**, not a thread id: the chip's row types a bare `gh-merge merge` because
  the queue that verb walks is GitHub's, so the merge never sees the message. Hence the branch
  in `PR_REVIEW_SUBJECT` + branch, matched exactly (the prefix alone names the *kind* and would
  sweep every waiting review). It runs after the merge and before the sync — a sync that fails
  leaves work on the maintainer's clone, not a request still awaiting a reviewer — and is
  best-effort like every other spool call, with a chip nudge only when a row actually went.
- **`summary`**, when the progress page contradicts what is recorded as solved
  (`UNREGISTERED_SUBJECT`): `mark` records a problem solved the moment its own results
  confirm the answer, which can be long before the answer is given to projecteuler.net. The
  import keeps the local record — it only ever *adds* solved problems — and reports the
  problems whose answers were never registered upstream. Prose, so the verb is a plain read.

### 13.8 The kit

`scripts/setup/msg.sh`, modelled on `smtp.sh` — the closest existing sibling, being a small
single-purpose service with its own uid and no Caddy route. Actions `deploy | remove |
upgrade | redeploy | status | help`; `upgrade` is an alias of `deploy`, like auth's and
smtp's. It creates the `euler-msg` user and group, generates `/etc/euler/msg.env`
(`root:euler-msg 0640`), and installs the root-owned unit. It does **not** own
`/opt/euler` — `auth.sh` does — so `msg.sh redeploy` only restarts.

The unit is harder than auth's, because this service needs nothing off the socket layer:

```
Type=simple
User=euler-msg
SupplementaryGroups=euler-web          # push to the per-user sockets; chgrp its own
StateDirectory=euler-msg               # /var/lib/euler-msg, 0700
StateDirectoryMode=0700
RuntimeDirectory=euler-msg             # /run/euler-msg, 0700 — its own admin plane
RuntimeDirectoryMode=0700
RestrictAddressFamilies=AF_UNIX        # cannot reach the network at all
IPAddressDeny=any
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/run/euler               # the shared socket dir; tmpfiles owns it
MemoryDenyWriteExecute=true
```

There is no `After=`/`Wants=` on `euler-auth`: the spool never talks to it, so the two
services have no ordering relationship to declare. `require_venv` refuses a deploy when
`solver.web.msg` is not importable from `/opt/euler`, which is the one way this kit can
fail confusingly — the venv belongs to `auth.sh`, and a checkout newer than the venv would
otherwise install a unit that crash-loops on `ModuleNotFoundError`.

`firewall.sh` still folds `euler-msg` into the egress drop set. The unit hardening already
makes off-host traffic impossible, so this is defence in depth: the nftables chain is
policy-accept, and an un-enumerated uid would reach the internet directly if the unit were
ever loosened.

## 14 · Security posture

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
not assign `admin` to a web identity (§6.5), so this requires an out-of-band root edit —
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
- **Master-key gate to master**: `git-push` on `master` needs `admin` and force-pushing it
  is refused unconditionally; a collaborator's work lands only via `gh-merge merge`, which a
  maintainer may run but only for a pull request confined to `solutions/` — never one
  touching `keys/`, the scripts or the framework. `git-publish` sits at `maintainer` so a
  maintainer can publish an enc-key grant they just made, and that does **not** widen the
  gate: `scripts/git/publish.sh` pushes `master` directly only when the authenticated
  GitHub user is the repo owner, and routes everyone else to a branch plus a pull request.
  The two legs are independent — a profile check on `git-push`, a GitHub-identity check in
  the publish script — so weakening either alone still leaves `master` closed.
- **Network posture**: only Caddy is network-bound; the app tier is loopback-only
  (systemd `IPAddressDeny` + host nftables); all egress — including every dynamic
  per-user uid, enumerated by the `euler-user` group — via the Squid allowlist.
- **Cookies**: `Secure; HttpOnly; SameSite=Lax`, site-wide.
- **The message spool is off the auth process** (§13.1): attacker-authored free text lives in
  `euler-msg`, which holds no verifiers, sessions or tickets, is unreachable from the edge,
  and is `AF_UNIX`-only. Message bodies stay plaintext-with-autoescape — no markdown or HTML
  renderer is added to that path — and its identity stays `SO_PEERCRED`, never a header or a
  body field.
- **The browser cannot write to the spool** (§13): the per-user tier serves one read-only
  chip fragment and the delivery push, and holds no write route at all. Every message and
  reply arrives over `msg.sock` from a uid the kernel vouched for, so the command's floor is
  the only gate. Adding a compose or reply route would move that boundary into the web tier
  for the first time.

## 15 · Operating it

Every service ships the same kit — `deploy` / `remove` / `status` (plus `upgrade` and
`redeploy` where they mean something), config generation, and a health probe that reports
actually-serving rather than "process exists". Because the units live in **root's** systemd
and run as locked-down `euler-*` users, lifecycle needs **`sudo`**.

The verbs are deliberate, and the Makefile target's verb is always the action its script
takes. **Local** things the terminal solver needs — apt packages, the `.venv`, git hooks,
completions, Chrome, Claude Code — are `install` / `uninstall`. **System** things the web
stack needs are `deploy` / `remove` / `redeploy`, because they touch root's systemd, the
`euler-*` identities, and `/etc/euler` rather than your checkout.

### 15.1 Deploy

```bash
echo 'EULER_TLS_DOMAIN=euler.example.com' >> ~/.euler/env   # if not already set
make deploy-web    # frontend → egress → ddns → firewall → smtp → auth → msg → user
```

Or per kit: `make deploy-frontend | deploy-egress | deploy-ddns | deploy-firewall |
deploy-smtp | deploy-auth | deploy-msg | deploy-user`. Every kit's `deploy` is idempotent, so
re-running it is the safe way to re-assert a drifted host.

`~/.euler/env` is the **deploy-time authoring source of truth**, read by the deploy path
(repo owner + sudo), which deploys **scoped** runtime config into `/etc/euler`. That
scoping is the point: `euler-ddns` sees only the DNS credentials, `euler-smtp` only the
Gmail ones, and no runtime service ever reads the full file. It carries
`EULER_TLS_DOMAIN`, the DNS provider credential pair (default `NAMEDOTCOM_USERNAME` /
`NAMEDOTCOM_TOKEN`), `SMTP_ADDRESS` / `SMTP_APP_PASSWORD`, and the operator's own
`ANTHROPIC_API_KEY`. The provider is selectable via `$EULER_TLS_DNS_PROVIDER` (default
`namecom`; also `cloudflare`, `route53`, `godaddy`, `digitalocean`, `gandi`).

Register the first admin account with `users add`.

### 15.2 Redeploy versus upgrade

**`make redeploy-web`** is the everyday turnaround after a source change: it pushes new
code, templates, and static assets without touching identities, units, certs, or the
firewall. `auth.sh redeploy` reinstalls the repo into the shared `/opt/euler` venv,
`user.sh redeploy` bounces running instances so their sockets re-activate them against
the rebuilt venv and re-lays each clone's per-clone setup from the operator's checkout, and `frontend.sh redeploy` refreshes `/etc/euler/web-content` plus the
Caddyfile and reloads the edge. It is **gated on `make check-version`** (its first
prerequisite): the version `solver/version.py` names — the number this build bakes into
the venv — must have its `vX.Y.Z` tag on origin, or the redeploy refuses. That stops a
release that was bumped and tagged locally but never pushed from running the deployed venv
ahead of what any collaborator clone can `git-sync` to.

**Per-clone setup travels with the redeploy.** Two things inside a collaborator's clone are
laid down from *this* checkout rather than by them: their git hooks, and their crypt filter's
command. Both are things they cannot receive any other way. A clone keeps whatever filter
command was recorded the day it was wired, and only `git-filter install` rewrites it — which
needs the master key, so it runs in their own session and nowhere else; writing the command,
though, needs no key at all (only the re-checkout does), so the operator can push it. It has
to carry **`-P`**: git runs a filter with the cwd at the top of the worktree, and a solver
checkout has a `solver/` package sitting right there, so without it the filter imports the
*clone's* source instead of the venv's — a clone that falls behind then runs an old filter
against a current key file and stops decrypting. An unwired clone is left alone; wiring it is
theirs to do when they are issued a key.

**Cutting a release.** The version is one tracked file, `solver/version.py`, written only
by `scripts/version/release.sh` (`make release`): it derives the SemVer bump from
Conventional Commits, rewrites the file, commits, tags `vX.Y.Z`, and **pushes the commit +
tag to origin** (`ARGS=--dry-run` previews, `ARGS=--no-push` stops before publishing). The
deployed venv is only as current as the last release baked into it, so the full flow is
**`make release` → `make redeploy-web`** — the push in the first step is exactly what
lets `check-version` pass in the second. A new web-shell *command* additionally needs each
per-user clone to `git-sync` and the terminal to reconnect before it appears (the
persistent PTY builds its command registry at spawn; see § 12).

Reach for **`make upgrade-web`** only when identities, units, or the Caddy/acme packages
themselves change. Note that systemd units are re-laid by `user.sh upgrade`, **not** by
`redeploy` — a unit change needs the upgrade path.

`upgrade` is the one verb that is not uniform, because for most kits there is nothing for
it to do that `deploy` does not already do:

| kit | `upgrade` |
|---|---|
| `frontend.sh`, `egress.sh` | Genuinely distinct: upgrades the Caddy / acme.sh / Squid **packages** and regenerates config + unit, without issuing a cert. |
| `auth.sh`, `smtp.sh`, `msg.sh`, `user.sh` | An alias of `deploy` — the deploy path is already the re-assert path. |
| `ddns.sh`, `firewall.sh` | No `upgrade` action at all; their `deploy` is idempotent and doubles as one, which is why `upgrade-web` calls `deploy-ddns` and ends on a `firewall.sh reload`. |

`make remove-web` tears the stack down in reverse; the kits prompt before deleting
state.

### 15.2.1 Status

**`make status-web`** is the read-only counterpart: it runs every kit's `status` in
deploy order — edge, egress, DDNS, firewall, mail relay, auth service, message spool,
per-user tier — and never changes anything. It needs `sudo` all the same, because what it reads is
root-owned (nftables, `/etc/euler`), the clones sit under `0700` homes, and the shell
report is a query on each running instance's own socket.

The last section is the collaborator roster, keyed on the **unix name** — the slug, which
is equally the uid, the home, the socket and the unit instance — with the **e-mail as an
alias**. The alias is looked up, not read off the name: the slug is a hash, so the report
recomputes `system_slug` over every identity in `/etc/euler/authorizations.json` and
indexes by the result. A slug with no alias is an account the policy no longer maps.

```
  ue0f4a1    vikas.munshi@gmail.com (admin)
             uid ✓ · clone ✓ · hooks ✓ · socket ✓ listening · service ✓ running
             web shell ✓ live · connected (1 terminal(s)) · pid 41207
  ufc2398    alice@example.com (contributor)
             uid ✓ · clone ✓ · hooks ✓ · socket ✓ listening · service … idle (socket-activated on demand)
             web shell … none (instance idle)
```

Read the two shell facts separately: **live** means that user's persistent PTY shell is
running (it survives a closed laptop — see § 12), and **connected** means a browser
terminal is attached to it right now. A live-but-`NOT connected` shell is normal and
shows how long it has been detached; the reaper collects it after the TTL.

An idle `service` is likewise not a fault — instances are socket-activated, so a
collaborator who is not browsing has no process. That is also why the shell query is only
made for a *running* instance: dialing the socket is what starts one, and a status
command must not fork a service for every idle invitee. The instance answers on
`GET /internal/status` over its own socket — socket-peer only, and Caddy answers
`/internal/*` with 404 rather than routing it.

### 15.3 Going public

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

### 15.4 Renewal

acme.sh runs as non-root `euler-acme` on a daily timer; its `--reloadcmd` fixes the key
mode and reloads via Caddy's admin API. Renewal needs no DNS credentials re-supplied —
acme.sh saved the token in the cert `.conf` at issue time. Force one with `frontend.sh
renew`. Each kit's `status` reports unit + health; `frontend.sh status` also shows cert
expiry and `/healthz`.

### 15.5 Configuration summary

| Layer | Key config |
|---|---|
| Authoring source | `~/.euler/env` (repo owner reads; installer deploys scoped copies) |
| Edge | `/etc/euler/Caddyfile` (`0644`), `/etc/euler/tls/server.{crt,key}` (setgid, key `0640`), `/etc/euler/web-content` |
| Egress | `/etc/euler-proxy/{squid.conf,squid.allowlist}`; client `HTTPS_PROXY` in `/etc/euler/egress.env` |
| Firewall + relay | `/etc/euler/nftables.conf`; `/etc/euler/smtp.env` (`root:euler-smtp 0640`) |
| Auth | `/opt/euler/venv`; `/etc/euler/auth.env` (`root:euler-auth 0640`); `/var/lib/euler-auth` (`0600`) |
| Messaging | `/etc/euler/msg.env` (`root:euler-msg 0640`); `/var/lib/euler-msg` (`0700`) |
| Policy | `/etc/euler/authorizations.json` (`root:root 0644`) |
| Per-user tier | `/etc/euler/user.env` (no secrets); `/home/<slug>/` (`0700`) |
| Sockets | `/run/euler/*.sock` (`0660 euler-<svc>:euler-web`); `/run/euler-adm/auth-admin.sock` and `/run/euler-msg/admin.sock` (`0600`, one per admin plane) |

### 15.6 Verify

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
