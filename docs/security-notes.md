# Security notes — accepted risks & regression guards

The standing security posture of the self-hosted web server: the risks we
**accept by design**, and the controls that are **sound and must not regress**.
It is the companion to the two build guides —
[secure-web-server.md](secure-web-server.md) (transport + infrastructure) and
[access-control.md](access-control.md) (identity + authorization) — and replaces
the point-in-time `security-assessment.md` (whose findings were either fixed or
concern code the redesign deleted; see [History](#history)).

Keep this short. A new *accepted* risk earns an `AR-NN`; a control we rely on
earns a line under [Regression guards](#regression-guards). Anything actionable
belongs in a guide or an issue, not here.

## Threat model in one paragraph

A home-hosted service whose whole point is to run a `solver` shell for invited
collaborators — **remote code execution is a feature, not a bug**. TLS
([secure-web-server](secure-web-server.md)) secures the channel; the auth service
([access-control](access-control.md)) gates *who* gets in; the invite list is the
real trust boundary. The design therefore spends its effort on **blast-radius
containment** (isolated service users, loopback-only app tier, kernel egress
firewall, secrets off the operator uid) rather than pretending the shell is not a
shell.

## Accepted risks

### AR-1 · A `contributor`+ login is host code execution

A `contributor`-profile account (or above) can `edit` a solution and `evaluate` it —
that runs arbitrary Python on the host. `claude-skill` (`maintainer`) launches a
headless agent with host tool access. Gating `!`/`bash` to `admin` in
`authorizations.json` does **not** contain this: the effective trust boundary is *who
receives which profile*, not the command policy.

**Why accepted, and narrowed (DD-11/DD-13).** The service exists to run collaborators'
code. The profile ladder **bounds** it: `reader` (the default invite tier) is
**read-only** — its web terminal (attach = `solver:execute`, DD-13) registers only the
read commands plus the shell's safe expression evaluator (no calls / attribute
access): no `eval`/`benchmark`/`edit`, no shell escape — so a new/untrusted invitee
triggers **no host execution of user code**; and `admin` (infra: `git`/`key`/`users`)
is **local-only**, so no web account can administer accounts or touch the crypto
master key. Execution of user code is thus confined to `contributor`+.
The redesign then **contains** what remains: each web shell runs as its rung's
dedicated `euler-ws-<profile>` uid (not the operator; DD-12/DD-13), from the
`/opt/euler` venv (DD-5), loopback-only with a kernel egress firewall (DD-8), so a
compromised shell reaches neither the operator's home, the crypto private key
(`~/.euler/id`), nor the open internet. Identity never rests
on the uid (DD-9/DD-11), so same-uid compromise cannot masquerade to the auth service.
**Standing controls:** grant `contributor`+ deliberately, keep the invite list audited;
keep `!`/`bash` `admin`-only and `claude-*` `maintainer`+ in the decorator `requires`;
do not widen the `euler-ws@` units' `ReadWritePaths`/egress or the `euler-sol-*` ACL
sets. Per-user helper uids or namespaces remain a future hardening (Phase 6).

### AR-2 · The web tier serves decrypted private solutions — a web compromise reads all current private plaintext

**This is a deliberately-accepted _high_ risk.** The content service reads the repo
working tree (DD-12), where the git filter leaves `solutions/private/**` **plaintext at
rest**. Every authenticated account — `reader` included (uniform read, DD-11) — can read
it through the viewer; `contributor`+ can write it. So a compromise of any web service (and
the web shell is RCE **by design**, AR-1) exposes **all current private-solution
plaintext**.

**What is *not* exposed — the containment.** The web tier does **no git operations** and
therefore **never holds the master key** (`~/.euler/id`, used only for commit/checkout,
stays with the operator locally, DD-12). So a web compromise gets the *current decrypted
files* but **not** the key: it cannot rotate, forge ciphertext, decrypt history not
checked out, nor read the far larger encrypted corpus straight off GitHub. The blast
radius is "the current working tree's plaintext," not "encryption-at-rest is defeated
forever" (the SEC-01 class, which *is* avoided).

**Why accepted.** A shared solver over the invited set is the product intent, and the
operator chose web-serves-private with this trade-off explicit. **Standing mitigations:**
the invite list is the trust boundary; per-profile uids + content-tree ACLs (DD-12)
contain write/delete; the DD-8 loopback egress firewall means a compromised service has no
arbitrary off-host path to exfiltrate in bulk (only via an attacker's own authenticated
session). **If the exposure is later judged too high, the knobs are:** serve
`solutions/private` to `contributor`+ only (make private-read part of graduating from
`reader`), or restrict private to the local terminal entirely (public-only web) — either
narrows or removes this risk.

### AR-3 · `euler-git` (Phase 7) is a second master-key holder — its compromise is key compromise

Accepted **in design** ([DD-15](secure-web-server.md#dd-15--secrets-are-brokered-never-dispensed));
takes effect when Phase 7 builds the git broker. `euler-git` holds its own X25519
keypair with a wrapped entry in `keys/enc-key.json` (plus a contents-scoped GitHub
PAT) so a `maintainer` can commit/push from the web with **no key on any web uid**.
Unlike AR-2 — where a web compromise reads only current working-tree plaintext — a
compromise of the `euler-git` *process* yields the master-key class (SEC-01):
decrypt the full encrypted corpus, forge ciphertext.

**Why accepted.** The alternative that delivers the same feature — key material on
the web tier — is strictly worse (AR-1's RCE tier would hold it). The broker
concentrates the risk in a service that is **not web-reachable** (no Caddy route;
a unix socket whose `SO_PEERCRED` allowlist admits only the `euler-ws-maintainer`
uid), runs **no caller-supplied input as paths, refs, or code** (four
strictly-typed verbs: `status`, `commit {n, message}`, `push` to `refs/heads/web/*`
only, never `--force`, and `restore {n}` — the sole working-tree write,
path-scoped to problem *n*'s `solution_dir` from the local `master` ref), never
switches branches or pulls (HEAD and the operator's index are untouched), and is
**loopback + Squid only** under the DD-8 firewall.
Enrollment is an explicit operator act (`user-authorize` + committing
`enc-key.json`) and is revocable: `key-rekey` rotates the master key and drops the
broker's entry. **Standing controls:** keep both brokers off Caddy; never widen the
verb surface toward caller-supplied paths/refs (`restore` stays scoped to a single
problem's directory); keep the PAT contents-scoped to this repo; keep master
merges of `web/*` a local, operator-reviewed act.

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
- **Identity is unforgeable** (DD-9): Caddy strips client `X-User`/`X-Profile`;
  web shells prove identity by a single-use ticket, not env; the local admin
  fallback requires the checkout-owner uid.
- **Wheel-gated admin plane** (DD-6): the admin socket is `0600` euler-auth-private;
  the token lives only in root-readable `auth.env`; `users` runs under `sudo`.
- **Secret hygiene**: auth state `0600`, `euler-auth`-only, off the operator uid;
  the crypto private key `~/.euler/id` `0600` outside the repo; no secrets in logs
  (auth access logs are disabled — tokens travel in query strings).
- **Network posture**: only Caddy is network-bound (`:443`); the app tier is
  loopback-only (DD-8, systemd `IPAddressDeny` + host nftables); all egress via the
  Squid allowlist.
- **Cookies**: `Secure; HttpOnly; SameSite=Lax`, site-wide.

## History

`security-assessment.md` (2026-07-06) was a point-in-time review of the **parked**
web server. Its findings are retired: SEC-01 (path traversal), SEC-04 (XFF
spoofing), SEC-05 (edge headers/CSP), SEC-07 (`.env` perms) were fixed; SEC-01/03/08
concern `solver/web/app.py` / `routes.py`, which the ground-up redesign
([secure-web-server](secure-web-server.md)) replaced. The two design-level risks
survive here as [AR-1](#ar-1--a-contributor-login-is-host-code-execution)
and [AR-2](#ar-2--the-web-tier-serves-decrypted-private-solutions--a-web-compromise-reads-all-current-private-plaintext).
