# Security notes — accepted risks & regression guards

The standing security posture of the self-hosted web server: the risks we
**accept by design**, and the controls that are **sound and must not regress**.
It is the companion to the build guides —
[secure-web-server.md](secure-web-server.md) (transport + infrastructure),
[access-control.md](access-control.md) (identity + authorization), and
[real-multi-tenant-web-access.md](real-multi-tenant-web-access.md) (the delivered
per-**user** model, the design of record for the multi-tenant web tier) — and
replaces the point-in-time `security-assessment.md` (see [History](#history)).

Keep this short. A new *accepted* risk earns an `AR-NN`; a control we rely on
earns a line under [Regression guards](#regression-guards). Anything actionable
belongs in a guide or an issue, not here.

## Threat model in one paragraph

A home-hosted service whose whole point is to run a `solver` shell for invited
collaborators — **remote code execution is a feature, not a bug**. TLS
([secure-web-server](secure-web-server.md)) secures the channel; the auth service
([access-control](access-control.md)) gates *who* gets in; the invite list is the
real trust boundary. The design therefore spends its effort on **blast-radius
containment** — each collaborator is their **own uid** with their own home, clone,
branch, and vault (MT-4/MT-5), the app tier is loopback-only behind a kernel egress
firewall, and no operator secret rests on any web-reachable uid — rather than
pretending the shell is not a shell.

## Accepted risks

### AR-1 · A `contributor`+ login is host code execution

A `contributor`-profile account (or above) can `edit` a solution and `evaluate` it —
that runs arbitrary Python on the host. `euler-solve` (`maintainer`) launches a
headless agent with host tool access. Gating `!`/`bash` high in
`authorizations.json` does **not** contain this: the effective trust boundary is *who
receives which profile*, not the command policy.

**Why accepted, and contained (MT-4/MT-5).** The service exists to run collaborators'
code. The profile ladder **bounds** it: `reader` (the default invite tier) is
**read-only** — its terminal (attach = `solver:execute`) registers only the read
commands plus the shell's safe expression evaluator: no `eval`/`benchmark`/`edit`, no
shell escape — so a new invitee triggers **no host execution of user code**. The
per-user model then **contains** what remains: every web session runs as that
collaborator's **own** `euler-user-<slug>` uid (systemd instance, no setuid), in
their own `0700` home and clone, from the root-owned `/opt/euler` venv (DD-5),
loopback-only with a kernel egress firewall (DD-8). A compromised session reaches
*that user's* home — never the operator's, never another user's (see AR-7 for what
"their own" includes). Identity never rests on the uid (DD-9): Caddy strips client
identity headers, shells prove identity by a single-use ticket, and the per-user
instance refuses a mis-slugged request. **Standing controls:** grant `contributor`+
deliberately, keep the invite list audited; keep `reader` free of every
code-execution command (`!`, `evaluate`, `claude-*` all sit at `contributor` — in
the per-user model raw bash grants nothing that `evaluate`'s arbitrary Python did
not already, and the AI spend is the user's own key); do not widen the
`euler-user@` unit's sandbox or the firewall's per-user egress lock.

### AR-2 · A web session reads the private plaintext **its user** is authorized for

The per-user model **narrowed** this risk (it was: *any* web compromise reads all
current private plaintext, uniformly). Each collaborator's instance serves **their
own clone**, and `solutions/private/**` in that clone is **ciphertext at rest until
the operator key-authorizes them** (MT-1/MT-2): a provisioned clone is born with the
git filter unwired, and only `user-authorize` + their own `git-sync` turns it to
plaintext. Private-plaintext visibility is therefore **per-person and revocable**
(`key-rekey`), orthogonal to the profile ladder.

**What remains accepted:** a compromise of an *authorized* user's session reads the
private plaintext in *that user's* worktree — the deliberate cost of a shared solver
over an invited set. **Standing mitigations:** the invite list plus the deliberate
`user-authorize` act gate who ever holds plaintext; per-user uids keep one user's
compromise out of every other tree; the DD-8 egress lock leaves no arbitrary
off-host exfiltration path. (An authorized user's uid also holds *key* access — that
stronger, distinct risk is [AR-5](#ar-5--a-key-authorized-users-uid-holds-master-key-access).)

### AR-3 · ~~`euler-git` broker as a second master-key holder~~ — retired, never built

Phase 7's credential brokers (`euler-ai`, `euler-git`) were designed
([DD-15](secure-web-server.md#dd-15--secrets-are-brokered-never-dispensed)) and then
**dropped** in favour of the per-user model: users bring their **own** keys (their
own Anthropic key in their vault, their own X25519 key in `enc-key.json`, their own
gh login for git), so there is no shared service secret to broker. The risk this
entry accepted never materialised; what replaced it is
[AR-5](#ar-5--a-key-authorized-users-uid-holds-master-key-access) (per-person
instead of one broker process). DD-15 stays in the design log as the reasoning that
led to the pivot.

### AR-4 · `admin` is web-reachable (MT-10a)

Authorization is by **profile only** (MT-10): the channel axis is gone, so an
`admin` account signed in over the web can run the highest-privilege operations —
`users` mutations, `user-authorize`, `key-rekey`, `git-merge` — that were previously
local-terminal-only (DD-11). **Why accepted:** in the per-user model the containment
that matters is the uid + SRP + the profile grant, not which keyboard the request
came from; the admin's session is exactly as strong as their SRP password + the
invite-gated account. **Standing controls:** keep the `admin` profile assigned to
the operator alone; the admin-plane socket stays wheel-gated under `sudo` (DD-6);
`infra:execute` commands never widen to lower rungs.

### AR-5 · A key-authorized user's uid holds master-key access

`user-authorize <pubkey>` wraps the crypto **master key** to that collaborator's
X25519 key in `keys/enc-key.json`. From then on **their uid can unwrap it** — the
SEC-01 class: decrypt the full private corpus (including straight off GitHub), forge
ciphertext. This is the deliberate MT-2 inversion of DD-15: the key holder is the
*person*, not a broker.

**Why accepted.** It is the product: a trusted collaborator who works on private
solutions needs exactly this power, and proof-of-possession (their key, in their
uid-private vault) is the cleanest form of it. The act is **per-person, explicit,
and revocable**: authorization is an admin running `user-authorize` (never
self-service; the same trust gate as the invite), and `key-rekey` rotates the master
key and re-wraps only to still-authorized keys — the de-authorized user's next pull
decrypts nothing. **Standing controls:** authorize named, trusted people only; treat
`enc-key.json` changes as audited events (they are commits); run `key-rekey` on any
doubt; the user's private key lives vault-encrypted (AR-6) in their `0700` home.

### AR-6 · The vault is at-rest opacity only (MT-6a)

A user's secrets (`~/.euler/id`, `~/.euler/env`) are envelope-encrypted under a key
derived from **their password**, which never reaches any server (SRP + a
browser-derived `PK`), so the operator cannot read them **at rest** — and a password
*reset* visibly destroys the vault rather than quietly re-keying it (MT-6c, no
covert operator backdoor). But the secrets are *used* server-side (the git filter,
`claude-api` — in the user's own session), so at time of use the vault key and
plaintext are in that session's memory. **A malicious active root can read that
memory or alter the shared solver code** — no design protects a secret from the
entity that controls the CPU it runs on. The guarantee is precisely: *encrypted at
rest, opaque to a passive/honest operator; not protected against a malicious active
root*. This is the same boundary the operator's own master key has always lived
with. Do not over-claim "zero-knowledge".

### AR-7 · `eval`/`benchmark` run untrusted solution code **as the user** (MT-6b)

A solution file is arbitrary code, and the runner executes it in the user's own
session — the same uid that holds their unlocked vault. A malicious solution can
therefore read *its own runner's* secrets: the session `VK`, their Anthropic key,
and (if key-authorized) the master key. **Why accepted:** the blast radius is **the
user themselves** — different uids keep it away from every other user and the
operator, which is the normal property of any shell that runs untrusted code as
you; egress is still Squid-gated. Sandboxing `eval` in a lower-privilege sub-uid or
namespace is the standing future hardening (the same one AR-1 defers).

## Regression guards

Sound controls — treat as invariants, not open work. A change that weakens any of
these needs a matching decision here.

- **SRP-6a** (`solver/web/auth/srp.py`): the password never reaches the server or
  disk; correct `PAD`, `u≠0` / `A,B mod N≠0` checks, `secrets.compare_digest`
  throughout. Cross-tested against the browser client (`tests/test_srp_interop.py`).
- **Anti-enumeration**: stable decoy salt/`B` for unknown emails at
  `/auth/challenge`; generic responses from `/forgot` and every invalid-token page.
- **Invite-only registration** (DD-7): single-use, **hashed**, time-boxed link
  tokens + a live-mailbox OTP; the account written is the invite's bound email,
  never client-supplied.
- **Remember-me**: selector\:validator with rotation-on-use, theft detection (a
  wrong validator revokes the selector), and `HMAC(validator)` at rest.
- **Identity is unforgeable** (DD-9/MT-11): Caddy strips client
  `X-User`/`X-Profile`/`X-User-Slug` and routes on the slug `forward_auth` returns;
  the per-user instance refuses a request whose `X-User` maps to another slug; web
  shells prove identity by a single-use ticket, not env; the local admin fallback
  requires the checkout-owner uid.
- **Wheel-gated admin plane** (DD-6): the admin socket is `0600` euler-auth-private;
  the token lives only in root-readable `auth.env`; `users` runs under `sudo`.
- **Secret hygiene**: auth state `0600`, `euler-auth`-only, off the operator uid; a
  user's `id`/`env` **vault-encrypted at rest** in their `0700` home (MT-6); the
  session `VK` lives only in a `0600` uid-private tmpfs file whose *path* is
  exported — the key itself is never in any process environment (MT-12); logout and
  reset remove it; no secrets in logs (auth access logs are disabled — tokens travel
  in query strings).
- **Ciphertext by default** (MT-13): a provisioned clone is born filter-unwired, so
  `solutions/private/**` rests as ciphertext until the deliberate `user-authorize`;
  `gitfilter install` verifies key access **before** wiring anything.
- **Master-key gate to master**: pushing `master` needs `infra:execute`;
  force-pushing it is refused unconditionally; a collaborator's work lands only via
  the admin's `git-merge` review gate (MT-2).
- **Network posture**: only Caddy is network-bound (`:443`); the app tier is
  loopback-only (DD-8, systemd `IPAddressDeny` + host nftables); all egress —
  including every dynamic `euler-user-*` uid, enumerated by prefix — via the Squid
  allowlist.
- **Cookies**: `Secure; HttpOnly; SameSite=Lax`, site-wide.

## History

`security-assessment.md` (2026-07-06) was a point-in-time review of the **parked**
web server. Its findings are retired: SEC-01 (path traversal), SEC-04 (XFF
spoofing), SEC-05 (edge headers/CSP), SEC-07 (`.env` perms) were fixed; SEC-01/03/08
concern `solver/web/app.py` / `routes.py`, which the ground-up redesign
([secure-web-server](secure-web-server.md)) replaced. The two design-level risks
survived as AR-1 and AR-2.

The **multi-tenant redesign** (2026-07-14/15,
[real-multi-tenant-web-access.md](real-multi-tenant-web-access.md)) replaced the
per-profile shared-uid web tier (DD-13) with per-user instances and dropped the
Phase-7 brokers (DD-15): AR-1 and AR-2 were reworked to the per-user containment
above, AR-3 was retired unbuilt, and AR-4–AR-7 record the model's new accepted
risks (admin-over-web, per-person key holders, the vault's at-rest-only boundary,
and eval-as-the-user).
