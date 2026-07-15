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
- **Authorization** — what a proven identity may do. A single **profile** on a
  four-rung ladder (`reader` → `contributor` → `maintainer` web-side, `admin` local
  only) drives command and route availability (DD-11).
- **Administration** — minting invites, promoting/demoting, and enabling/disabling
  accounts, over a sudo-gated local admin plane.

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
| Web user re-execs `solver` with a chosen `SOLVER_USER` | env is display-only; identity requires a single-use ticket |
| `reader` web shell `unset SOLVER_TICKET; solver` to gain `contributor` | a `euler-*` service uid without a ticket **aborts** — the non-owner→`contributor` fallback is for real logins only (DD-11 §4.5) |
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
   the page: the email (read-only), the **Terms of use** in a scroll box (the
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
   /register/complete`, which also carries the account's **display name** (Phase 7:
   used for web-git authorship, editable later at `/account`). On a `verified`
   record this creates the `users.json` entry (with the recorded Terms acceptance
   and name), **consumes** the pending record, and lands on `/login` (no
   auto-login).

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

The browser client (`solver/web/content/assets/srp.js`) interoperates byte-for-byte with
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

`solver/auth` (`resolve_subject`) resolves the `Subject` (user, channel, auth_method,
profile, permissions) **once** at startup, with no anonymous fallback:

| Plane | Voucher | Mechanism |
|---|---|---|
| Web request | auth service | SRP session cookie → `forward_auth` → `X-User` + `X-Profile` |
| Web shell (PTY child) | auth service | **one-time shell ticket**, redeemed over `auth.sock` |
| Local terminal | the OS | `os.getuid()` **owns the repo checkout** → `admin`; a real non-owner login → `contributor` |

**The shell ticket.** Every web shell runs as its rung's shared
`euler-ws-<profile>` uid (DD-12/DD-13), and `/proc/<pid>/environ` is
same-uid-readable — so nothing env-carried can be the credential (a sibling
shell on the same rung could replay it). Instead: on WS attach the ws service
forwards the user's session cookie to `POST /shell-ticket`, which mints a
**single-use, 60-second** ticket bound to `(email, profile, display name)` — the
name rides along for web-git authorship
([DD-15](secure-web-server.md#dd-15--secrets-are-brokered-never-dispensed), Phase 7);
the forked child
redeems it at startup (`POST /shell-ticket/redeem`), which consumes it and returns
the authoritative identity. Missing/expired/reused → the shell aborts; so does a
redeemed profile that differs from the per-profile ws instance's `EULER_PROFILE`
pin ([DD-13](secure-web-server.md#dd-13--web-shell-topology--gating)). Minting needs
a live cookie the shell user does not hold; the `/shell-ticket*` endpoints are not
routed by Caddy (socket-peer only).

**Local terminal.** The profile is the `authorizations.json` `users`-map value for the OS
login (DD-12) — the same map that carries web emails. The **checkout owner is seeded
`admin` at install**, and if the owner is somehow absent from the map the owner-uid still
floors to `admin` (you cannot lock yourself out of your own checkout); an explicit entry
wins, so the operator *can* deliberately run local at a lower profile. `admin` (infra:
`git-*`/`key-*`, plus `users:write`) is reachable only locally, never over the web (DD-11).
A `euler-*` **service uid without a ticket aborts**, so a `reader` web shell cannot `unset
SOLVER_TICKET` and re-exec `solver` as `euler-ws` to escalate. The old assume-an-identity
path (`SOLVER_USER` / `keys/.user-email` / env) is gone; `SOLVER_USER` is display-only.

Resolution order: `SOLVER_TICKET` set → redeem (failure aborts); else a `euler-*` service
uid → `SystemExit`; else `users.get(os_login)`; else owner-uid floor → `admin`; else
`contributor`.

## 5 · How authorization works

Authorization runs on **one RBAC kernel — `solver/auth` — shared by the shell and the
web** (DD-12), from one policy file `authorizations.json`. A command/route declares the
permissions it *needs*; the policy declares what each *profile has*; enforcement is the
subset check. Two orthogonal axes narrow a command to its context:

| Axis | Question | Driven by | Enforced at |
|---|---|---|---|
| **Channel** | is the command valid in this channel? | the decorator's `channels=(terminal,web)` | registration (`solver/auth` + the decorator) |
| **Permission** | does the profile hold what the command requires? | the decorator's `requires=[obj:perm]` vs `authorizations.json` profile grants | registration (shell) / app router (web) |

`modules.csv` is now a **pure loader manifest** (`module, registers_commands`) — the old
`terminal`/`web` columns moved to the per-command `channels=` axis, so `update-docs`
(`channels=('terminal',)`) never registers in a web shell and `!` (`shell:execute`) never
registers for a profile lacking it.

### Profiles (the four-rung ladder, DD-11)

Every identity carries one profile, resolved at startup (§4.5) and exposed as
the subject's `profile` (DD-12). The ladder, most→least privileged:

| Profile | Reached by | Gains over the rung below |
|---|---|---|
| **reader** | web invite (default) | **view** — docs, the full solution tree (public + decrypted private), assets |
| **contributor** | web (promoted), or a local non-owner login | + **edit** solutions + **execute** (eval/benchmark in the web terminal; the terminal itself attaches at `reader` via `solver:execute`, DD-13) |
| **maintainer** | web (promoted) | + **delete** solutions + AI commands (`claude-*`, owner's budget) |
| **admin** | **local terminal only** (checkout owner) | + infra: `git-*`, `key-*`, `users`, `manage-config`. **Never web-assignable.** |

`admin` reachable only by owning the checkout means no web account can administer
accounts or touch the crypto master key. `reader` is a **stepping stone** — a new
invitee starts read-only and is promoted (`users change`, §6) as trust grows. Read
scope is uniform: every account, `reader` included, may read the decrypted
`solutions/private` plaintext (the [AR-2](security-notes.md) posture).

### The policy file (`authorizations.json`)

The ladder is expressed as **RBAC grants**, not a per-command CSV (`commands.csv` is
retired, DD-12). `authorizations.json` (deployed to `/etc/euler`, read by shell and
services) has `profiles` (grants + single-parent `inherits`), `users` (email/os-login →
profile), and `objects` (permission namespace → filesystem paths):

```json
{
  "ladder": ["reader", "contributor", "maintainer", "admin"],
  "users":  { "vikas.munshi@gmail.com": "admin", "mercanther@gmail.com": "reader" }
}
```

**Re-simplified (the multi-tenant model):** authorization is a **plain profile
ladder**. A command/route declares its *minimum profile*
(`@register(requires='contributor')`), and enforcement is a rank comparison
(`reader < contributor < maintainer < admin`). A command with **no `requires`**
defaults fail-closed to `admin`, so a new command is never silently exposed. The
earlier `object:permission` grant sets and the `objects`→paths map existed to
drive per-path filesystem ACLs on the shared operator tree — the per-user model
(every collaborator in their own clone, as their own uid) retired that layer, so
the policy file carries exactly one decision: **who has which profile**. The
ladder itself is structural and lives in code
(`solver/auth/subject.py::LADDER`); the file's `ladder` field documents it and is
validated on load. Example floors: `show`/`ls`/`git-status`/`git-sync`/`user`/
`vault` → `reader`; `new`/`edit`/`evaluate`/`benchmark`/`!`/`claude-*`/
`git-commit`/`git-push`/`git-identity` → `contributor` (their own uid sandbox,
their own Anthropic key, their own `user/<slug>` branch; master lands only via
the admin's `git-merge`); web file-delete → `maintainer`; `users` mutations/
`key-rekey`/`user-authorize`/`git-merge`/`git-publish`/`manage-config` → `admin`
(`users list` registers at `reader` but self-scopes to the caller's own entry,
MT-10b). `update-docs` regenerates the audit table in
**`docs/authorizations.md`** — module / command / minimum profile for every
command, distinct from the authored `authorizations.json`.

### Enforcement (shell + web)

- **Shell (decoration time):** as each command module imports, the decorator checks
  `channel ∈ channels` and `requires ⊆ subject.permissions`. If not permitted the command
  is **not registered** — invisible to `?`/help/completion, `unknown command` (exit 127)
  if invoked. One process serves one identity, so the set is fixed for the process's life.
- **Web routes:** the content service gates each route with `requires(<capability>)` on the
  requester's `X-Profile` — the **same policy**, so `authorizations.json` is the single
  source across both surfaces. The DD-11 matrix (view / edit / delete / execute) is the
  contract. A **per-profile OS layer** (per-profile service uids + content-tree ACLs,
  DD-12) sits behind the app check on the web.

(The content service is not yet built; this is the contract it will honour.)

## 6 · Administration (the `users` command)

`users` is split by verb (DD-12): **`users list`** requires `users:read` (a `reader`+
grant) and reads the world-readable `/etc/euler/authorizations.json` roster; the
**mutating verbs** require `users:write` (`admin`) and go through the **wheel-gated admin
plane** (DD-6) — the CLI (`solver.web.auth.admin`) re-executed under `sudo`, editing the
root-owned SoR. So an ordinary operator process can *list* but not *change*.

```bash
users list                                    # roster (reader+); full account state needs admin
users add alice@example.com                   # WEB: mint + email an invite (default profile: reader)
users add bob@example.com contributor         # WEB: invite a contributor
users add vikas admin                         # LOCAL: a bare os-login → direct map entry, no invite
users change alice@example.com contributor    # promote/demote — the stepping-stone verb
users disable alice@example.com               # also kills live sessions + remember tokens
users enable  alice@example.com
users remove  alice@example.com               # delete the account/entry and any pending invites
```

**Two-path `add`** (DD-12): an `@`-address is the **web** path — the CLI (as root) writes
`authorizations.json[email]=profile` **and** mints an emailed invite (rolled back if the
mail fails); a bare **os-login** is the **local** path — just the map entry, no invite (a
local login authenticates by *being* that OS user). Web-assignable profiles are `reader`
(default) / `contributor` / `maintainer` — **`admin` only for a local os-login**, never a
web account. `change` rewrites the map and, for a web account, **revokes live sessions +
remember tokens** so the new profile takes effect on next login — and (Phase 6)
the same auth-service paths **push a teardown to any live web shell**, so a
running PTY's baked-in permissions die immediately, not at next login
([DD-14](secure-web-server.md#dd-14--web-shell-lifecycle--revocation)). No reset verb — reset is
self-service (§4.1). Mutating verbs prompt for `sudo`.

## 7 · Reference

### State (`/var/lib/euler-auth`, `euler-auth`-only `0600`)

| File | Purpose |
|---|---|
| `users.json` | SRP verifier DB: `{salt, verifier, name, terms_version, terms_accepted_at, created, disabled}` per email — `name` is the display name (captured at registration, editable at `/account`; used for web-git authorship, DD-15/Phase 7) — **no profile** (it lives in `authorizations.json`, DD-12). `euler-auth` resolves the profile fresh from the map at each login (`AuthService.profile_for`), capped at `maintainer`, defaulting `reader` when unmapped. |
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

### Runtime config

- **`/etc/euler/auth.env`** (`root:euler-auth 0640`): `EULER_BASE_URL`,
  `EULER_ADMIN_TOKEN` (root-only), `TERMS_VERSION`, `EULER_SMTP_RELAY`. Deployed from the
  authoring source `~/.euler/env` by `scripts/setup/auth.sh`; the auth service never reads
  the full `~/.euler/env` (no Anthropic key, no SMTP creds — mail via the loopback relay,
  DD-8).
- **`/etc/euler/authorizations.json`** (`root:root 0644`, DD-12): the authorization
  system of record — `profiles` / `users` / `objects`. World-readable (non-secret policy),
  **root-write only**; mutated exclusively through the sudo-gated `users` path. Read by
  both the local shell and the app services.

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
5. Masquerade (all verified, Phase 6): a request with a forged `X-User` header is
   ignored — Caddy strips it and the upstream sees only the `forward_auth` value; a
   bare `solver` run as a `euler-*` service uid with no ticket aborts at startup; the
   web-shell **ticket is single-use** (a replay from a sibling shell's
   `/proc/<pid>/environ` is dead on arrival); and a ticket whose profile differs from
   the forking instance's `EULER_PROFILE` pin aborts, so no cross-profile attach.
