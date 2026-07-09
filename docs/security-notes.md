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
headless agent with host tool access. Gating `!`/`bash` to `admin` in `commands.csv`
does **not** contain this: the effective trust boundary is *who receives which
profile*, not the command policy.

**Why accepted, and narrowed (DD-11).** The service exists to run collaborators' code.
The profile ladder **bounds** it: `reader` (the default invite tier) is **read-only —
no execute, no web shell**, so a new/untrusted invitee triggers no host execution; and
`admin` (infra: `git`/`key`/`users`) is **local-only**, so no web account can administer
accounts or touch the crypto master key. Execution is thus confined to `contributor`+.
The redesign then **contains** what remains: the web shell runs as the dedicated
`euler-ws` uid (not the operator), from the `/opt/euler` venv (DD-5), loopback-only with
a kernel egress firewall (DD-8), so a compromised shell reaches neither the operator's
home, the crypto private key (`~/.euler/id`), nor the open internet. Identity never rests
on the uid (DD-9/DD-11), so same-uid compromise cannot masquerade to the auth service.
**Standing controls:** grant `contributor`+ deliberately, keep the invite list audited;
keep `!`/`bash` `admin`-only and `claude-*` `maintainer`+ in `commands.csv`; do not widen
the `euler-ws` unit's `ReadWritePaths`/egress. Per-user helper uids or namespaces remain
a future hardening (Phase 6).

### AR-2 · Web auth grants plaintext read of all private solutions

Every authenticated account — **`reader` included** (read scope is uniform, DD-11) —
can read the **decrypted** `solutions/private/` tree through the viewer; `contributor`+
can also write it. This relaxes the project's "plaintext never leaves the repo" rule to
"plaintext is served to any authenticated web account," and there is no per-user
isolation on the solution tree.

**Why accepted.** A shared solver is the intent; the invite list bounds the audience,
and a `reader` is still an invited account. If compartmentalisation is ever wanted, the
knobs are: gate `solutions/private/**` to `contributor`+ (make private-read part of
graduating from `reader`), or add per-solution ownership/ACLs. Documented here rather
than enforced. (The content viewer/editor lands in Phase 5; this note precedes it so the
decision is explicit before that surface exists.)

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
and [AR-2](#ar-2--web-auth-grants-plaintext-read-of-all-private-solutions).
