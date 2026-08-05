# SRP Guide — proving a password without sending one

This guide covers **Secure Remote Password (SRP-6a)**, the protocol behind every web login:
the mathematics it rests on, and exactly how this project uses it. It is implemented twice,
deliberately — [`solver/web/auth/srp.py`](../solver/web/auth/srp.py) for the service and
[`solver/web/content/assets/srp.js`](../solver/web/content/assets/srp.js) for the browser —
and the two are held byte-for-byte compatible by
[`tests/test_srp_interop.py`](../tests/test_srp_interop.py).

SRP gates **web access**. It does not unlock the solution encryption: that is the master key
([Git Filter Guide](gitfilter-guide.md), [Secret Sharing Guide](secret-sharing-guide.md)) and
the per-user vault ([Vault Guide](vault-guide.md)), which share no key material with the login.
The one thing the two worlds share is the account's SRP **salt**, reused as the vault's KDF
salt — §8.

---

## 1. The problem it solves

A conventional login sends the password to the server, which hashes it and compares. Three
things follow, all bad and none fixable by hashing harder:

- the server **receives** the password, so every request handler, log line, proxy and crash
  dump is a place it can leak from;
- the server **stores** something derived from it, so a stolen database is an offline cracking
  exercise against every user at once;
- the client cannot tell whether it is talking to the real server, only that something on the
  far end accepted the password it just gave away.

SRP removes all three. The password never leaves the browser. What the server stores is a
**verifier** `v = g^x mod N`, where recovering `x` — and through it the password — is a discrete
logarithm in a 2048-bit group. And the handshake is **mutual**: the server proves it holds a
verifier for that account before the client accepts the session.

The cost is that a password reset cannot recover anything, because the server has nothing to
decrypt with. That is a consequence of the design rather than an oversight, and it is why a
reset here destroys the vault
([Vault Guide §7](vault-guide.md#7-password-reset-destroys-the-vault)).

---

## 2. Parameters

| parameter | value | where |
| --- | --- | --- |
| group `N` | RFC 5054 Appendix A, 2048-bit safe prime | `srp.py:_N`, `srp.js:N_HEX` |
| generator `g` | 2 | `_g` |
| hash `H` | SHA-256 | throughout |
| multiplier `k` | `H(PAD(N) ‖ PAD(g))` — SRP-6a, computed once | `_k` |
| salt | 16 random bytes | `_SALT_BYTES` |
| `PAD(·)` | left-pad an integer to 256 bytes — the byte length of `N` | `_pad` / `pad` |
| version tag | `srp6a-sha256-2048` | `VERSION` |

`N` is a *safe* prime: `N = 2q + 1` with `q` prime, so the multiplicative group mod `N` has only
four subgroup orders — `1`, `2`, `q`, `2q`. There is nowhere small to be pushed into except the
order-2 element, which the `A mod N ≠ 0` / `B mod N ≠ 0` checks and the `PAD`-ed hashing already
make useless. In this group `g = 2` generates the full group of order `2q` (`pow(2, q, N) ≠ 1`),
which is why the parameters are taken verbatim from RFC 5054 rather than chosen here.

**`PAD` is the interop contract.** Every integer fed to a hash — `A`, `B`, `S`, `N`, `g` — is
left-padded to 256 bytes first. Hashing an integer's minimal big-endian encoding instead would
make the digest depend on how many leading zero bytes the value happened to have, so one
endpoint would disagree with the other for roughly one login in 256. The Python and JavaScript
implementations therefore pad identically, and the interop test exists to keep them that way.

`VERSION` is stamped into every stored token. It names the hash *and* the group, so a future
parameter change is a new version string with a migration, not a silent reinterpretation of
existing verifiers.

---

## 3. Registration: the verifier

The browser picks a random 16-byte salt `s` and derives

```
x = H( s ‖ H(email ":" password) )          (RFC 5054 §2.6)
v = g^x mod N
```

then sends **`{salt, verifier}`** to the server, which stores exactly that and nothing else
(`UserRecord.salt`, `UserRecord.verifier`, both hex, in the auth service's own `users.json`).
The password and `x` never exist outside the browser.

The inner `H(email ":" password)` binds the verifier to the account name, so the same password
under two addresses yields unrelated verifiers. The outer hash with the salt is what stops one
precomputed table covering every user.

`x` is deliberately cheap to compute — two SHA-256 calls. SRP's security against a stolen
verifier database is the discrete log, not the KDF: `v = g^x mod N` cannot be inverted, and an
attacker guessing passwords must run a modular exponentiation per guess. The defence in depth
against weak passwords is a **length and class policy**, enforced in the browser because the
server cannot see the password to check it:

| policy | value | source |
| --- | --- | --- |
| minimum length | 16 characters | `policy.MIN_PASSWORD_LENGTH` |
| required classes | lower + upper + digit + special (all four) | `policy.PASSWORD_REQUIRE_CLASSES` |

Server-side, registration validates only *shape* — a 32-hex-character salt and a non-zero
verifier of at most 512 hex digits (`pages.py:flow_complete`, and identically in
`app.py:password_change`). It cannot do more, and pretending otherwise would be theatre.

**What gates registration is therefore not the password but the mailbox.** `POST
/register/complete` accepts `{token, salt, verifier}` only for a pending record already in the
`verified` state: an emailed invite link (`INVITE_TTL_SECONDS`, 7 days) plus a six-digit
one-time code proving live mailbox control at completion time (`OTP_*` in `policy.py`). The
token is single-use — `pending.consume`.

---

## 4. The handshake

```
client (knows password)                             server (knows salt, v)

a ← random, A = g^a mod N        ──── email ───▶
                                 ◀── salt, B ───    b ← random, B = (k·v + g^b) mod N
u = H(PAD(A) ‖ PAD(B))                              u = H(PAD(A) ‖ PAD(B))
x = H(salt ‖ H(email:password))
S = (B − k·g^x)^(a + u·x) mod N                     S = (A · v^u)^b mod N
K = H(PAD(S))                                       K = H(PAD(S))
M1 = H(H(N)⊕H(g) ‖ H(email) ‖ salt
       ‖ PAD(A) ‖ PAD(B) ‖ K)    ──── A, M1 ──▶     recompute M1, compare
                                 ◀───── M2 ─────    M2 = H(PAD(A) ‖ M1 ‖ K)
check M2
```

### Why both sides reach the same `S`

The server's side, substituting `v = g^x`:

```
S_server = (A · v^u)^b = (g^a · g^(x·u))^b = g^(b·(a + u·x))
```

The client's side, substituting `B = k·v + g^b = k·g^x + g^b`:

```
B − k·g^x = g^b        so      S_client = (g^b)^(a + u·x) = g^(b·(a + u·x))
```

Identical — but only if the `x` the client derived from the typed password matches the `x`
behind the stored verifier. A wrong password gives a wrong `x`, hence a different base on the
client side, hence a different `S`, hence an `M1` the server rejects. Nothing about *how* wrong
the password was leaks: the failure is one comparison of two 32-byte digests.

### What each term is for

- **`k = H(PAD(N) ‖ PAD(g))`** is what makes this SRP-**6a**. Without it `B` would be a plain
  Diffie-Hellman public value, and an active attacker could send `B = g^b`, sidestepping the
  verifier entirely. Blending `k·v` into `B` forces the client to subtract a term it can only
  compute from the password.
- **`u = H(PAD(A) ‖ PAD(B))`** is the scrambling parameter, derived from *both* ephemerals
  rather than chosen by either. A `u` the server could pick freely would let a malicious server
  run a dictionary attack against the client's response.
- **`M1` includes `H(N)⊕H(g)`, the email and the salt**, so a proof is bound to this group, this
  account and this handshake — it cannot be replayed into a session for another user or another
  parameter set.
- **`M2 = H(PAD(A) ‖ M1 ‖ K)`** is the server's answer, and checking it is what makes the
  authentication mutual. `srp.js` computes the expected `M2` before it ever posts `M1`, and
  `check(m2)` compares — a phishing front end that does not hold the verifier cannot produce it.

### The rejections in the code

| check | where | why |
| --- | --- | --- |
| `B mod N ≠ 0` | `SrpClient.process_challenge` | a zero `B` forces `S = 0` on the client — a server that sends it learns the client's proof for a known key |
| `A mod N ≠ 0` | `SrpServer.verify` | likewise `S = 0` server-side: an attacker could authenticate with no password at all |
| `u ≠ 0` | `_compute_u` | `u = 0` drops the verifier out of the server's exponent |
| digest comparison | `secrets.compare_digest` | constant-time, so proof comparison leaks no timing |

Every one of these is a real SRP attack, and each is one line. They are also why the handshake
objects raise `ValueError` rather than returning a boolean: an invalid protocol value is not a
wrong password, and the two must not share a path.

---

## 5. Where it runs in this project

```
browser                     Caddy            euler-auth (unix socket)
────────                    ─────            ───────────────────────
srp.js                                       solver/web/auth/
  computeVerifier()  ──register──▶ TLS ──▶     app.py     endpoints + challenge table
  startLogin()                                 srp.py     the protocol
    POST /auth/challenge {email}               users.py   salt + verifier at rest
    ◀── {salt, B}                              policy.py  lifetimes and rules
    POST /auth/verify {email, A, M1}           ratelimit.py
    ◀── {M2}, session cookie set
```

| endpoint | body in | body out | notes |
| --- | --- | --- | --- |
| `POST /auth/challenge` | `{email}` | `{salt, B}` | `AuthService.start_challenge`; one in-flight handshake per email |
| `POST /auth/verify` | `{email, A, M1}` | `{M2}` + session cookie | `finish_challenge`; the challenge is consumed whether or not it succeeds |
| `POST /register/complete` | form `{token, salt, verifier}` | redirect to `/login` | `pages.py`; the invite+OTP gate above, single-use token |
| `POST /auth/password` | `{A, M1, salt, verifier}` | `{M2}` | signed-in change: the **same handshake** re-used as proof of the current password, in one atomic exchange with the new verifier |

That last row is worth noticing as a pattern: SRP is not only a login here. Where the server
needs to know that the person at the keyboard knows the *current* password, it runs the
identical handshake as a re-authentication step — because the one thing it cannot do is ask for
the password and compare. On success every other session and all remember-me tokens are revoked
and any live web shell is torn down; the session that made the change stays signed in.

Four properties of the service side are worth stating, because each answers an attack the
mathematics alone does not:

**Unknown accounts get a decoy.** `decoy_token(email, secret)` derives a *stable* salt and a
plausible verifier by HMAC-SHA256 from a per-process secret (`secrets.token_bytes(32)` at
service start) and the email. An unregistered address therefore gets a challenge of the right
shape, with a salt that does not change between attempts within a run, and the proof simply
fails at the next step. Without it, `/auth/challenge` would be an account-enumeration oracle —
and a *random* decoy salt would be one too, since a real account's salt is stable. Nothing is
stored: the decoy is recomputed on demand and reveals nothing about real users.

**Challenges are single-use and short-lived.** The server ephemeral `b` is held in memory keyed
by email, expires after `CHALLENGE_TTL_SECONDS = 120`, and is `pop`ped at verify time. Reusing
`b` across handshakes would weaken the exchange; keeping challenges indefinitely would be an
unbounded memory hole reachable by an unauthenticated caller.

**The account state is re-read after the proof.** `finish_challenge` re-checks that the user
exists and is not disabled *after* verifying `M1`, because the admin plane may have disabled the
account during the two round-trips.

**Rate limiting sits in front.** `AUTH_RATE_MAX = 30` per `AUTH_RATE_WINDOW_SECONDS = 60` per
client on the unauthenticated endpoints (`ratelimit.py`) — which is what turns "an attacker must
exponentiate per guess" into "and may only guess 30 times a minute".

### After a successful proof

The profile comes from `/etc/euler/authorizations.json` (`profile_for`, loaded fresh so a
`users change` takes effect at the next login, defaulting to `reader`), and the response sets:

| cookie | constant | lifetime |
| --- | --- | --- |
| `solver_session` | `policy.SESSION_COOKIE` | 12 h, in-memory table — a service restart drops it |
| `solver_remember` | `policy.REMEMBER_COOKIE` | 30 days, rotating selector/validator token (`remember.py`), optional |

Caddy then authenticates every subsequent request through the auth service's `forward_auth` and
routes by `X-User-Slug` — see [web-server-guide.md](web-server-guide.md).

---

## 6. Using the module directly

Both ends are ordinary Python objects, so a handshake can be run in-process — which is what
`verify_password` does for the paths where the password genuinely is available locally (tests,
a local harness):

```python
from solver.web.auth.srp import SrpClient, SrpServer, SrpToken, make_srp_token, verify_password

token = SrpToken.parse(make_srp_token('ada@example.com', 'correct horse battery staple'))

server = SrpServer('ada@example.com', token)          # holds the verifier
client = SrpClient('ada@example.com', 'correct horse battery staple')
m1 = client.process_challenge(server.salt, server.public)
m2 = server.verify(client.public, m1)

client.verify_session(m2)                             # True — mutual
client.session_key == server.session_key              # True — same K
verify_password('ada@example.com', 'nope', token)     # False, and raises nothing
```

`SrpToken` serialises as `<version>$<salt-hex>$<verifier-hex>`; the user store keeps the two
fields separately but round-trips through the type (`UserRecord.srp_token`).

The shared key `K` is a by-product here: the session is a cookie, not a `K`-keyed channel,
because TLS already carries confidentiality. `K` matters as the thing both proofs are bound to —
if it ever becomes a channel key, it is available and already agreed.

---

## 7. Interoperability and tests

`tests/test_srp_interop.py` runs the **actual browser client** under Node (skipped when Node is
absent — `make install-nodejs`) against the Python server: register in JS and verify in Python,
challenge in Python and respond in JS. It is the only test that can catch a padding,
normalisation or byte-order drift between the two implementations, and any change to either file
must keep it green.

Two normalisation rules are part of the wire contract and easy to break:

- the **email is trimmed and lower-cased** on both sides (`normalizeEmail` / `normalize_email`)
  before it enters `x` and `M1`, so the store key and the hashed identity agree;
- integers cross the wire as **hex without a `0x` prefix**, `A` and `B` unpadded (they are
  re-padded before hashing), the salt as fixed 32 hex characters.

`srp.js` defines `globalThis.SRP` idempotently: htmx re-injects the script when the
change-password fragment swaps in a second time, and a top-level `const` would throw on the
second execution.

---

## 8. What SRP does *not* do here

- **It does not unlock the encryption.** The master key that decrypts `solutions/private/` lives
  in `~/.euler/enc-key.json`, wrapped to an X25519 key, and reaches a new collaborator as a
  sealed half plus the half their clone already carries
  ([Secret Sharing Guide](secret-sharing-guide.md)). A login has no path to any of it.
- **It does not protect against a malicious server.** SRP proves the far end holds a verifier;
  it cannot stop the code that holds it from being changed. That boundary is the same one the
  [Vault Guide](vault-guide.md#1-what-it-is-and-what-it-is-not) states.
- **It is not a KDF for anything** — except in one deliberate reuse: the account's **SRP salt is
  also the vault's PBKDF2 salt**, so the browser can derive the vault password key `PK` from a
  password it already holds and a salt it already received in the challenge, with no second
  round-trip and no second secret. The two systems still share nothing else — the salt is public
  by construction, and `x` (SRP) and `PK` (vault) are separate derivations from it.
- **It cannot recover a forgotten password.** A reset mints a new verifier and, because the old
  `PK` is gone with the old password, deliberately destroys the vault
  ([Vault Guide §7](vault-guide.md#7-password-reset-destroys-the-vault)).

---

## 9. Files

| file | role |
| --- | --- |
| [`solver/web/auth/srp.py`](../solver/web/auth/srp.py) | the protocol, both ends, plus `verify_password` and `decoy_token` |
| [`solver/web/content/assets/srp.js`](../solver/web/content/assets/srp.js) | the browser client (plain script, CSP `'self'`, also loadable under Node) |
| [`solver/web/auth/app.py`](../solver/web/auth/app.py) | `/auth/challenge`, `/auth/verify`, password change, the challenge table |
| [`solver/web/auth/pages.py`](../solver/web/auth/pages.py) | the register / reset / forgot flows, and `/register/complete` |
| [`solver/web/auth/users.py`](../solver/web/auth/users.py) | the service's own `users.json`: salt + verifier at rest, host-only |
| [`solver/web/auth/policy.py`](../solver/web/auth/policy.py) | lifetimes, cookie names, password and OTP rules |
| [`solver/web/auth/ratelimit.py`](../solver/web/auth/ratelimit.py) | sliding-window limiter on the unauthenticated endpoints |
| [`tests/test_srp_interop.py`](../tests/test_srp_interop.py) | JS ↔ Python interop, byte-for-byte |
