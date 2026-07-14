# Real multi-tenant web access — design of record

> **Status: design, converging.** This supersedes the web tier's per-*profile*
> shared-uid model ([secure-web-server.md](secure-web-server.md) DD-13) with a
> per-*user* one, and **replaces the dropped Phase 7 brokers** (DD-15). Instead of
> brokering secrets away from a shared RCE uid, we *invert* the problem: each user
> runs in their **own uid** with their **own keys**, so a user's secrets are exposed
> only to that user's own code. The JupyterHub / multi-tenant dev-environment shape,
> built almost entirely on primitives the project already has.
>
> Decisions are recorded as **MT-N**. Cross-references to the delivered design use its
> **DD-N**. Nothing here is built yet; this is the specification to build to.

## 1 · Why — the pivot

The delivered web front end (Phases 1–6) runs each web *rung* as one shared uid
(`euler-ws-<profile>`). The now-dropped Phase 7 existed only to work around the
consequence: **no secret can rest on a shared RCE uid** (a key readable by
`euler-ws-maintainer` is readable by every maintainer's shell), so the Anthropic key
and the crypto master key had to be reached through brokers, and identity/authorship
degraded to *claim-based* headers (the DD-9 same-uid reality).

The brokers are the symptom; the shared uid is the cause. **Give each collaborator
their own uid and the problem inverts**: their own key, in their own uid-private home,
used only by their own shell — which is not a leak, because they own it. Kernel
identity (`SO_PEERCRED`, real uids) replaces claim-based headers; per-user worktrees on
per-user branches make git native. This is a **real collaborative tool for an invited
set of trusted, named collaborators** — that framing is what makes §11's trade-offs
acceptable.

## 2 · Target shape

```
  browser ──TLS──▶ Caddy (edge) ──forward_auth──▶ auth service ─▶ email → user slug
                     │  routes EVERYTHING for a user to their one socket (by X-User-Slug)
                     ▼
   ONE per-user service, born as euler-user-<slug> (systemd, no setuid) — MT-5
     · serves the content routes AND the /ws shell for this user (MT-4)
     · reads the SHARED read-only solver app (/opt/euler), EULER_REPO_ROOT=~/euler (MT-3)
     home  /home/euler-users/<slug>/                       (0700, uid-private)
       ├─ euler/                the user's repo clone — CONTENT, branch user/<slug> (MT-3)
       │    └─ solutions/private/**  ciphertext until enc-key authorized (MT-2)
       └─ .euler/               the user's VAULT — secrets, opaque to the operator (MT-6)
            ├─ id                their X25519 private key, ENCRYPTED under the vault key
            ├─ env               their ANTHROPIC_API_KEY etc., ENCRYPTED
            ├─ vault             wrap(PK, VK): the vault key wrapped by the password key
            └─ user_pass         (terminal only) the password, to derive PK off-line

  Kept from the delivered design (MT-9): Caddy TLS edge · Squid egress · nftables
  firewall · euler-smtp (admin/auth mail only) · the RBAC ladder (authorizations.json).
```

Everything a user touches is theirs: uid, home, keys, clone, branch. Their Anthropic
key is their own billing; their commits are authored and pushed as themselves;
revocation is `key-rekey` + disabling the account.

## 3 · Two orthogonal trust layers — MT-1

Trust is **two independent dials**, and every combination is valid:

| Layer | Grants | Mechanism | Set by |
|---|---|---|---|
| **Ladder** `reader→contributor→maintainer→admin` | which *commands* you may run | `authorizations.json` (DD-12), unchanged | admin, at `users add` / `users change` |
| **enc-key** authorized / not | whether you can see **private-solution plaintext** | your X25519 public key wrapped into `keys/enc-key.json` (`user-authorize`) | admin, later, on request (§6) |

A `contributor`-without-key edits public problems and sees **ciphertext** for private
ones; a `contributor`-with-key can decrypt and edit private; a `reader`-with-key can
read private plaintext but not edit. The ladder is a **capability** gate; enc-key is a
**content-visibility** gate. They do not interact.

**This tightens [AR-2](security-notes.md).** Today every authenticated web account
reads all private plaintext (uniform read, shared working tree). Here private plaintext
requires an explicit, per-person, revocable key grant — so an un-graduated newcomer
sees only public solutions + ciphertext. The old `reader`-vs-`contributor` privacy line
is re-expressed, more precisely, as *enc-key authorized or not*.

## 4 · One per-user service — MT-4

A **single** systemd template instance per user — `euler-user@<slug>.service`,
`User=euler-user-<slug>` — serves *both* the content routes (problem pages, file
editor, progress) *and* the `/ws` shell for that user, all operating on their
`~/euler`. Caddy routes every request for a user to their one socket
(`/run/euler/user-<slug>.sock`) by the `X-User-Slug` that `forward_auth` returns — the
per-*user* analogue of today's `X-Profile`.

The delivered per-profile split (`euler-content@` + `euler-ws@`) existed only because
the shell was the RCE-risk service and content was read-mostly; **per-user uids make
that separation moot** — the isolation boundary is now the uid. One service kind, one
socket per user, N services instead of 2N.

**Born as the right uid, no setuid (preserves DD-2/DD-4).** Each instance is `User=`
the per-user uid; no process changes uid, no service runs as root. **Socket-activated**
(`euler-user@<slug>.socket`) so idle invitees cost nothing and systemd starts the
instance on first attach.

## 5 · Shared solver, per-user content — MT-3

The **`solver` application is shared and read-only** — one install everyone runs, the
existing `/opt/euler` venv (DD-5). The **content is per-user**: each user's `~/euler` is
their own git clone (solutions, docs, their branch, their edits, their results, their
`.state`). The shared app is pointed at the user's content with **`EULER_REPO_ROOT=~/euler`**
— the exact override added in Phase 6 (`solver/config.py` + `solver/crypto/config.py`).

This is why the folder layout is `~/euler` (clone) + `~/.euler` (secrets): `solver.config`
already derives the secrets dir as `root_dir.parent/.{root_dir.name}`, so a repo root of
`~/euler` yields a secrets dir of `~/.euler` with **no new path logic** — the private
key (`~/.euler/id`), env (`~/.euler/env`), and `.state` all fall into place per-user.

## 6 · The enc-key layer — per-user master-key access — MT-2

Reuses `solver.crypto` wholesale. The crypto **master key** is wrapped, per authorized
X25519 public key, in the tracked file `keys/enc-key.json` (proof-of-possession: hold
the matching private key → unwrap the master key → smudge/clean).

- **Each user has their own X25519 keypair.** The private key lives in their vault
  (`~/.euler/id`, §7); the public key is enrolled by an admin with `user-authorize`.
- **Authorization is a deliberate admin trust act** — it grants decryption of the
  *whole* private corpus, so it is never self-service. Flow: the user generates their
  key in their web shell (`user`), reads their public key off the account page (§9),
  and passes it to an admin **out-of-band**; the admin runs `user-authorize <pubkey>`,
  **commits and pushes** `keys/enc-key.json`; the user **`git pull`s** into `~/euler`
  and their key now unwraps the master key. **The distribution channel is git itself** —
  no side channel.
- **Revocation** is `key-rekey` (rotate the master key, re-wrap only to still-authorized
  keys) + push; the de-authorized user's next pull can no longer decrypt.
- **Cloning lands ciphertext.** Provisioning (§8) clones with the smudge filter
  **disabled**, so `solutions/private/**` is ciphertext at rest in the user's home — a
  user who is not yet key-authorized *cannot* read private plaintext even though the
  files are in their own home. Once authorized (+ pull), a re-checkout smudges to
  plaintext. **The git filter enforces the enc-key layer for free.**

## 7 · The per-user vault — SRP-derived, at-rest opacity — MT-6

The vault makes a user's secrets **opaque to the operator at rest** — "your keys are
yours," not a file-permission fig leaf. Both `~/.euler/env` (Anthropic key, gh/other
secrets) and `~/.euler/id` (the X25519 private key) are stored **encrypted**.

**Envelope encryption (not direct password-encryption):**
- A random per-user **vault key `VK`** encrypts the secrets.
- `VK` is stored **wrapped** under `PK = KDF(password, salt)` — reusing the SRP salt —
  in `~/.euler/vault`.
- Use: derive `PK` → unwrap `VK` → decrypt secrets. **Rotation (change-password)
  re-wraps only the small `VK` blob** with the new `PK`; the secrets are never
  re-encrypted. Cheap and standard.

At rest the operator holds `{salt, verifier}` (auth), `wrap(PK,VK)`, and `VK`-encrypted
secrets — and can decrypt **none** of it without the password. SRP already guarantees
the password never reaches the server; `PK` is derived only where the password is known.

**Key delivery (MT-12, resolved).** The crypto that needs `VK` — `load_private_key`
and the git clean/smudge filter — runs as **subprocesses** (git spawns the filter per
file), so `VK` must be reachable by the user's child processes, not just the interactive
shell. Resolved as: `VK` lives in a **uid-private tmpfs file** (`0600`, e.g.
`$XDG_RUNTIME_DIR/euler/vk` or `/run/euler/vk-<slug>`), written at session start and
removed at session end; only its **path** is exported (`EULER_VAULT_KEY_FILE`), inherited
by subprocesses so the git filter finds it. The key itself is never in any process's
environment (so not in `ps e`, core dumps, or every child's `/proc/environ`) — only in
the tmpfs file and, transiently, in the memory of the code that decrypts. Where `VK`
comes from:
- **Web:** the browser derives `PK` at login (it has the password; the salt arrives in
  the SRP challenge — no extra round-trip) and passes it to the user's own service at
  shell-attach; the service unwraps `VK` and writes the tmpfs file. `PK`/`VK` never
  touch server disk. (The auth service *cannot* derive `PK` — it never sees the
  password — which is precisely what keeps the vault operator-opaque at rest.)
- **Terminal:** `~/.euler/user_pass` (uid-private) holds the password; the shell derives
  `PK` from it at start. Weaker (password at rest) but it is the terminal-convenience
  path, and the terminal user is typically the operator on their own box.

**The threat boundary, stated honestly (MT-6a).** The secrets are *used server-side*
(the Anthropic key by `claude-api`, the private key by the git filter — both in the
user's shell process), so at time of use `VK` and the plaintext are in server memory.
**A malicious root operator can always read that memory (ptrace) or modify the shared
solver code to exfiltrate.** No design protects a secret from the entity that controls
the CPU it runs on. The vault's guarantee is therefore precisely: **encrypted at rest
and opaque to a passive/honest operator; NOT protected against a malicious active
root.** This is the *same* boundary the master-key model already lives with (root could
always scrape the master key from a smudging process), so the vault is consistent with
the accepted posture — it extends at-rest opacity to the per-user secrets. The design
and [security-notes](security-notes.md) must state it in these exact terms; we do not
over-claim "zero-knowledge."

**Crypto-layer touchpoints.** `load_private_key` (`crypto/ciphers.py`) and `get_api_key`
(`ai/models.py`) stop reading plaintext and decrypt with the session `VK` (a
process-scoped secret set at shell start — from attach for web, from `user_pass` for
terminal). The vault is **orthogonal** to the master-key machinery: `user-authorize`
and `key-rekey` never need a *user's* private key, so the vault never interferes with
enrollment or rotation. A user can have a working vault yet no master-key access (their
pubkey simply isn't in `enc-key.json`) — MT-1 and MT-6 compose cleanly.

## 8 · Provisioning & lifecycle — MT-7

**Account creation is an admin act, terminal + sudo, with NO secrets** (DD-6 shape):

`users add <email> <profile>` (admin, sudo) →
1. create the system user `euler-user-<slug>` + home (`0700`);
2. clone the repo into `~/euler` **using the admin's git credentials**, filter
   **disabled** (ciphertext at rest, §6), checked out on a fresh branch `user/<slug>`;
3. lay down the socket-activated `euler-user@<slug>` unit + socket;
4. mint the web **invite** (SRP registration → the user sets their password → their
   vault `VK`/`wrap(PK,VK)` is initialised on first login, §7);
5. no keys, no Anthropic secret — those are the user's later, self-service steps.

**Later, self-service in the web shell:** `user` (generate keypair) → pubkey to admin
out-of-band → admin `user-authorize` + push → `git pull` (§6); `gh auth login` (their
own GitHub identity, to push `user/<slug>`); `claude /login` or an uploaded Anthropic
key via the account page. Each writes into the user's own vault.

**Teardown** (`users disable`/`remove`): stop + disable the instance, `key-rekey` to
drop the account's master-key access, archive or delete `~/euler` + `~/.euler`.

## 9 · The account page — MT-8

A per-user credential dashboard (served by the user's own service, so it can act on
their vault):
- **Public key** — shown, for the out-of-band `user-authorize` step.
- **Secrets** — upload / replace / **delete**, **write-only** (never rendered back;
  the stored form is `VK`-ciphertext anyway). Upload = the user provides the plaintext
  (over TLS, to their own service), which encrypts it under `VK` into `~/.euler/env`.
- **gh login status** — from `gh auth status`; the actual `gh auth login` runs in the
  web shell.
- **Claude Code login status** — likewise; `claude /login` runs in the web shell.

## 10 · Channel-agnostic authorization — MT-10

**Authorization is by profile only; the channel (terminal vs web) is no longer an
authorization axis.** In the per-user model the isolation boundary is the uid, not the
channel — a user's web shell is bash in *their own* sandbox, no different from their
terminal — so gating on `channels=` earns nothing. The decorator's `channels=`
parameter and the channel check in `is_permitted` are removed; `subject.channel`
survives **informationally** only (e.g. `show`/`edit` still branch browser-tab vs.
OSC-to-pane).

**Consequence — admin is web-reachable (drops DD-11 "admin is local-only") — MT-10a.**
`key-rekey`, `user-authorize`, `users`, and push-to-master become usable over the web
for an `admin`-profile account (whose gh identity is the repo owner, so it *can* work
master directly). This removes any hard dependency on physical/terminal access to the
box. The containment for those highest-privilege operations is now **the profile grant
+ SRP auth strength + per-user uid isolation**, with no channel backstop — an explicit,
accepted posture change (recorded as [AR-4](security-notes.md), §11).

## 11 · Threat model & accepted risks

The trust boundary remains the **invite list** — named, trusted collaborators. What
changes:

- **Gained:** kernel-authoritative per-user identity (no same-uid masquerade *between*
  users); per-user blast radius (a compromised shell reaches only *that* user's home,
  keys, clone); no operator secret on the web tier; private plaintext gated per-person
  (tightens AR-2); at-rest operator-opacity for user secrets (§7).
- **New accepted risks** (to record in [security-notes.md](security-notes.md)):
  - **AR-(key):** a key-authorized user's uid can unwrap the master key — the SEC-01
    class (decrypt the full corpus, forge ciphertext). Accepted per-person, revocable
    (`key-rekey`); gated by the deliberate `user-authorize` trust act.
  - **AR-4 (admin-over-web, MT-10a):** the highest-privilege operations are
    web-reachable; containment is the profile grant + SRP + isolation, not the channel.
  - **AR-(vault, MT-6a):** the vault is at-rest opacity only — a malicious active root
    can read a live session's memory; unavoidable when secrets are used server-side.
  - **AR-(eval, MT-6b):** `eval`/`benchmark` run untrusted *solution* code **as the
    user**, in the same uid that holds the vault — so a malicious solution can read the
    running user's own `VK`, Anthropic key, and (if authorized) master key. Blast radius
    is **the user themselves** (not other users — different uids), which is the normal
    property of any shell that runs untrusted code as you; egress is still Squid-gated.
    Sandboxing `eval` in a lower-privilege sub-uid / namespace is the future hardening
    (the same one AR-1 already defers).
- **Unchanged:** a collaborator's login is host code execution *as their own contained
  uid* (AR-1, now better bounded — their own sandbox, their own egress via Squid).

## 12 · Carries over vs. changes

| Delivered (Phases 1–6) | Multi-tenant |
|---|---|
| TLS edge, Squid egress, nftables firewall, `euler-smtp` (admin/auth mail) | **kept** (MT-9) |
| SRP auth service, `forward_auth`, sessions, invites/OTP | **kept**; resolves email → user slug; adds vault `VK` bootstrap at login |
| RBAC ladder `authorizations.json` (DD-12) | **kept** as the capability dial (MT-1) |
| Per-profile shared uids `euler-ws@`/`euler-content@` (DD-13) | **replaced** by one per-user `euler-user@<slug>` service (MT-4) |
| Shared working tree; master key never on the web tier | **replaced** by per-user clones; master key unwrapped per-user via each user's own authorized key (MT-2) |
| Uniform private-plaintext read (AR-2) | **tightened**: private plaintext gated per-user by enc-key (MT-1) |
| Channel-gated commands; `admin` local-only (DD-11/DD-13) | **dropped**: profile-only authorization; admin web-reachable (MT-10) |
| Shell ticket `(email, profile)`; claim-based headers | user identity → per-user uid; `SO_PEERCRED` authoritative |
| Plaintext `~/.euler/id`, `~/.euler/env` | **encrypted** in the per-user vault (MT-6) |
| DD-15 brokers (`euler-ai`, `euler-git`) | **dropped**: users bring their own keys; AI + git are native per-user |

## 13 · Build-plan sketch (subject to §14)

1. **Per-user vault in `solver.crypto`** (MT-6): envelope `wrap(PK,VK)`; `load_private_key`
   / `get_api_key` decrypt with a session `VK`; the `user_pass` terminal path; migration
   of the operator's own `~/.euler`.
2. **Per-user identity in `solver/auth`** (MT-3/MT-4): email → slug → uid/home; the web
   plane of `resolve_subject` resolves a *user*; drop the channel authorization axis (MT-10).
3. **Provisioning kit** (MT-7): `users add` extension (uid, home, filter-disabled clone
   on `user/<slug>`, socket-activated `euler-user@<slug>` unit); teardown.
4. **The per-user service** (MT-4): fold content + `/ws` into one `solver/web/user`
   service; Caddy `X-User-Slug` routing; retire the per-profile instances.
5. **The account page + vault UX** (MT-8/MT-9): pubkey, write-only secret upload/delete,
   gh + Claude-Code login status; `VK` delivery at attach.
6. **Per-user git** (MT-2): native `git-commit`/`git-push` on `user/<slug>` as the
   user; admin merges `user/*` → master (web or terminal); enc-key pull flow.
7. **Docs & security-notes**: the three new ARs (§11); retire DD-13/DD-15 as superseded.

**Clean-slate start (no migration).** The live per-profile deployment is removed with
`make uninstall-web` before the multi-tenant stack is installed; current web accounts
are recreated, not migrated (§14.5).

## 14 · Mechanics — resolved (verified against real tooling)

1. **Caddy per-user routing (MT-11) — verified.** A single Caddyfile routes to
   `reverse_proxy unix//run/euler/user-{http.request.header.X-User-Slug}.sock`, with
   `request_header -X-User-Slug` stripping any client copy and `forward_auth …
   copy_headers X-User-Slug` supplying the trusted value. Tested against Caddy **2.11.4**
   (the deployed version): a session routes to *its* user's socket, the **WebSocket
   upgrade survives** the placeholder upstream, a **forged `X-User-Slug` is stripped**
   (a user cannot reach another's socket), and no session → 401. No dynamic-upstream
   module needed — a request-header placeholder in the dial address suffices.
2. **`VK` delivery (MT-12) — resolved & verified.** Uid-private tmpfs file + inherited
   `EULER_VAULT_KEY_FILE` path (§7). Verified that a git clean/smudge **filter subprocess
   inherits** the delivery env from the shell → git → filter, so the filter can reach
   `VK` at checkout time.
3. **Disk & scale (MT-13) — verified.** Per-user `git clone --reference <shared-mirror>`
   points `objects/info/alternates` at a **shared read-only object store** (ciphertext
   blobs shared once); each user's clone carries only its own new commits, and the smudge
   runs **per-clone with that user's key** → plaintext only in their worktree. Confirmed:
   the reference clone shares objects and checks out plaintext with the key in the tmpfs
   file. Provisioning maintains one shared bare mirror refreshed from `origin/master`.
4. **Slug scheme (MT-14) — decided.** `solver/auth.slugify` emits `.` (e.g.
   `mercanther_gmail.com-3f9e97`), which **fails `useradd`'s `NAME_REGEX`**
   (`[a-zA-Z0-9_-]` only). The multi-tenant **system slug** is therefore a stricter
   derivation — `[a-z0-9-]`, letter-start, a sanitized+truncated local-part plus a short
   hash suffix, bounded so `euler-user-<slug>` stays well under the name limit (e.g.
   `euler-user-mercanther-3f9e97`, 27 chars). The email stays the login identity; the
   slug is the derived system identity used for the uid, home, socket, and `X-User-Slug`.

**Migration — none.** The per-profile deployment is torn down with `make uninstall-web`
and the multi-tenant stack installed fresh; existing web accounts are **recreated**, not
migrated (§8). Only the operator's own local `~/.euler` needs the one-time vault
migration (MT-6, build step 1). A hard reset, not an in-place upgrade.
