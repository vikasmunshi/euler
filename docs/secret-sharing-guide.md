# Secret Sharing Guide — splitting the master key

This guide covers **Shamir secret sharing**: the mathematics of `k`-of-`n` thresholds, and the
2-of-2 split this project uses to deliver the master key without ever putting the whole of it
in one place. It is implemented in [`solver/crypto/keys.py`](../solver/crypto/keys.py) (the
section headed *2 of 2 secret sharing*), and driven by `user-authorize`, `key-split` and
`key-reconstruct` — with `host-authorize` / `host-unlock` for the machines the split cannot
reach.

Related: [Git Filter Guide](gitfilter-guide.md) — what the master key opens;
[Vault Guide](vault-guide.md) — where the private key that opens a sent half lives;
[web-server-guide §6.3](web-server-guide.md) — the roster of public keys.

---

## 1. The problem

There is one master key. It encrypts every file under `solutions/private/`, and every
collaborator holds a copy in `~/.euler/enc-key.json`, wrapped to their own X25519 public key.
Granting it to somebody new means moving 32 bytes across a gap.

The obvious way is to wrap those 32 bytes to their public key and send them. That works, and it
has one property worth improving on: the message **is** the key to anyone who also holds the
recipient's private key. A stolen laptop, a restored backup of `~/.euler`, a forwarded message,
a spool database read by someone who should not have it — any two of those together is total
access to the private tree.

Splitting removes the single artefact. The key is cut in half; the halves live in different
places, protected by different things, and neither is worth anything alone.

| the artefact | where it lives | what protects it |
| --- | --- | --- |
| the local half | `/etc/euler/share.json` on the host | being on the host at all — and nothing else is needed (§2) |
| the sent half | one message in the spool, sealed to one public key | the recipient's private key |

An attacker needs the message, the private key that opens it, **and** the ability to read the
host. The collaborator needs exactly the same three, which is why this is not theatre: it is
the same act, arranged so no one piece is ever enough.

> **The half was tracked once, and that was a mistake.** It sat in the repository, on the
> argument that a single share reveals nothing — which is true (§2) and beside the point. This
> repository is **public**, so a half anybody can clone is not a factor at all: the sealed
> message plus the private key was the whole of the secret, exactly as with an issued key. It
> moved to the host so that the two halves are protected by different things again.

---

## 2. Shamir's scheme

### The idea

A polynomial of degree `k−1` is fixed by exactly `k` points, and by no fewer. Put the secret at
`t = 0`, hand out points elsewhere on the curve, and that is a threshold scheme: `k` shares
determine the polynomial and therefore `f(0)`; `k−1` determine nothing at all.

Everything happens in a finite field `GF(p)`, with `p` the 13th Mersenne prime

```
p = 2^521 − 1
```

comfortably larger than the 256-bit secret it carries. The field is not decoration. Over the
integers a share would leak the secret's *magnitude*; modulo a composite, division would not
always be defined. Over a prime field every non-zero element has an inverse — so interpolation
always works — and share values are uniform across the whole field, which is what makes a share
reveal nothing.

### Splitting

To split a secret `s` into `n` shares at threshold `k`:

1. take `a₀ = s`, and draw `a₁ … a_{k−1}` uniformly at random from `GF(p)`;
2. form `f(t) = a₀ + a₁t + a₂t² + … + a_{k−1}t^{k−1} mod p`;
3. pick `n` distinct **non-zero** `x` values and hand out the pairs `(xᵢ, f(xᵢ))`.

`x = 0` is never a share: that point *is* the secret.

### Reconstructing

Any `k` shares recover `s` by Lagrange interpolation evaluated at zero:

```
                 k                    −xⱼ
s = f(0) =      ∑   yᵢ ·    ∏      ─────────    (mod p)
                i=1        j ≠ i    xᵢ − xⱼ
```

Each product is the `i`-th Lagrange basis polynomial at 0 — it is 1 at `xᵢ` and 0 at every other
`xⱼ` — so the sum is the unique degree-`k−1` polynomial through all `k` points, read off at
`t = 0`. The division is a modular inverse (`pow(den, -1, p)`), which exists for every non-zero
denominator because `p` is prime, and the denominators are non-zero precisely because the `x`
values are distinct.

### Why `k−1` shares reveal nothing

This is the property the whole design rests on, and it is **information-theoretic**: it does not
weaken with time, hardware, or a break in some cipher.

Take any `k−1` shares and any candidate secret `s'`. Those `k−1` points plus `(0, s')` are `k`
points with distinct `x` values, so exactly one polynomial of degree `k−1` passes through them.
Every candidate secret is therefore consistent with what you hold — and each is consistent via
exactly one choice of the random coefficients, which were drawn uniformly. The posterior
distribution over `s` is the prior: uniform. The shares have told you nothing.

The corollary matters as much: the shares of a secret form an **unbounded family** — every point
on the curve is a valid share — and *any* `k` of them reconstruct. "2-of-2" below means the
threshold is two, not that only two shares exist.

### A worked example

Small enough to check by hand: `p = 97`, secret `s = 42`, threshold `k = 2`, random coefficient
`a₁ = 17`, so `f(t) = 42 + 17t mod 97`.

```
share A:  x = 3   →  f(3) = 42 + 51 = 93
share B:  x = 5   →  f(5) = 42 + 85 = 127 mod 97 = 30
```

Reconstruct from `(3, 93)` and `(5, 30)`, with `2⁻¹ = 49 mod 97`:

```
s = 93 ·  (−5)/(3−5)  +  30 ·  (−3)/(5−3)
  = 93 ·   5·49       +  30 ·  (−3)·49          (mod 97)
  = 93 ·   51         +  30 ·   47
  = 87 + 52 = 139 = 42                          (mod 97)   ✓
```

And the operation `key-split` actually performs — given the local share `(3, 93)` and the
secret, derive the *other* half — is the same line read the other way:

```
slope = (93 − 42) / 3 = 51 · 3⁻¹ = 51 · 65 = 17     (mod 97)
f(5)  = 42 + 17·5 = 30                              ✓ the same share B
```

---

## 3. The 2-of-2 as this project builds it

### Drawing the local half

`_random_share()` draws it with **no reference to the master key at all**:

```
x  ← uniform in [1, p)
y  ← uniform in [0, p)
```

That is not a shortcut, it is §2 read forwards. At threshold two, a secret's shares are one
uniformly random point plus the point the line through it and `(0, s)` demands — so whichever
half is drawn *first* is just a random point. Drawing the local one first makes it independent
of which key is current, and lets the other half be minted against whatever the master key is at
the moment somebody needs it.

### Minting the half that travels

`_counterpart(secret, share)` produces the half for one recipient:

```
intercept = int(secret)                                  # f(0) = the master key
slope     = (y₁ − intercept) · x₁⁻¹        (mod p)       # the line through (0,s) and (x₁,y₁)
x₂        ← uniform in [1, p), x₂ ≠ x₁                   # a fresh point every time
share₂    = (x₂, intercept + slope·x₂)     (mod p)
```

A fresh `x₂` per recipient means no two collaborators are ever handed the same bytes. Note what
§2's corollary says here: two recipients who pool *their* halves reconstruct the key with no
host access at all — which is fine, since each of them is entitled to it anyway.

### Sealing it

The counterpart is never sent in the clear. `_wrap_share` puts it in the **same envelope an
issued key rides in** — `ciphers.lock`: an ephemeral X25519 key, ECDH against the recipient's
public key, HKDF-SHA256, then ChaCha20-Poly1305 — so the message body carries a blob that only
that recipient's private key opens.

An earlier version sent the half in the clear, on the argument that a share alone reveals
nothing. It does — but everyone who can read the spool can also read the other half, so a share
in the clear was one artefact away from the master key for exactly that audience. Sealing costs
nothing and removes it.

### The wire format

A share is `x` and `f(x)`, each as 131 hex digits (`_HEX_WIDTH`: `⌈521/4⌉` covers any value below
`p`), concatenated — **262 lowercase hex characters**, fixed width, so the split point is
positional. Sealed, it becomes a longer run of hex (the ephemeral public key, the ciphertext,
the tag).

One pattern, `_SHARE_RE = [0-9a-f]{262,}`, finds either form in a message body, and
`_unwrap_share` tells them apart by shape: exactly 262 characters is a bare share, anything
longer is an envelope to open. The body needs no marker saying which it carries, and the manual
path still accepts a share handed over out of band.

### Proving the result

Reconstruction is arithmetic: wrong inputs yield a wrong answer, not an error. So the result is
proved before anything is written.

1. **Range.** The secret is 32 bytes while the field is ~521 bits, so a reconstruction from
   mismatched shares lands above `2²⁵⁶` with overwhelming probability and `_reconstruct_secret`
   raises. Cheap, and it catches gross mistakes.
2. **`verify`.** The share file carries the same fixed-plaintext ciphertext the enc-key file
   does — the opening quatrain of Blake's *Auguries of Innocence* (`config['verify_text']`) under
   the master key. Decrypting it back to the known text proves the reconstructed key **is** the
   master key. This is the check that matters, and it works on a machine with no enc-key file to
   compare against — exactly the machine doing the reconstructing.

Carrying `verify` beside the share also **dates the share to a key**, which is what lets
`key-split` recognise one drawn before a rotation (§6).

---

## 4. Where the local half lives

Operational state on the host, never repository content:

```json
{
  "share":  "<262 hex>",
  "verify": "<hex>",
  "since":  "2026-08-05T…Z"
}
```

Resolved in this order (`solver/crypto/config.py`):

| candidate | when |
| --- | --- |
| `$EULER_SHARE_FILE` | tests, and any machine that keeps it elsewhere |
| `/etc/euler/share.json` | a deployed host — the directory's existence is the test |
| `~/.euler/share.json` | a plain checkout with no deployed tier |

Two properties make this work without privilege:

- **everybody reads, one writer.** The deployed file is `root:root 0644`, beside
  `authorizations.json`. `key-split` computing a counterpart and `key-reconstruct` completing
  one both only *read* it, so a maintainer's web shell — which can never obtain `sudo` — grants
  exactly as it did before. Only the lay-down and the rotation redraw write, and `_write_local_share`
  falls back to `sudo install` for the root-owned path.
- **world-readable is not a leak.** A single share is a uniformly random point (§2). What
  changes by keeping it on the host is *who* holds it: not everyone with a clone of a public
  repository, but everyone with an account on the machine.

The public keys a half is sealed to live next door, in `/etc/euler/roster/users.json` — the
roster, world-readable and writable by `euler-maint`, carrying **no key material at all**. It
is the same floor for the same reason: whoever can write a public key there can redirect the
next grant to a key they hold. See [web-server-guide §6.3](web-server-guide.md).

---

## 5. Usage

### Laying the local half

Once per host, and again after every rotation:

```bash
key-split                   # maintainer; sudo when /etc/euler/share.json is the target
```

With no half yet — or one that predates the current master key — it writes it and **stops**:

```
No local share yet — written /etc/euler/share.json.
It stays on this host and is never committed. Now run
`key-split <identity>` to send the other half.
```

### Granting access, on the host

```bash
authorize <message-id>                  # the request their `user` command filed
authorize <public-key> <identity>       # or by hand, for a key that reached you otherwise
```

`user-authorize` is the whole grant: it takes the public key from the request thread, **records
it in the roster**, and delivers half the master key sealed to it. It refuses outright while the
local half is missing or stale — the one failure that cannot be discovered at the far end, since
`key-split` would lay a fresh half, report success, and leave the request dismissed as worked
with nothing delivered.

`key-split <identity>` is the same delivery without the request-thread handling, for a re-send
or a recipient who never filed one:

```bash
key-split <identity>                    # public key from the roster
key-split <identity> <public-key>       # …or given, for a first grant
```

Receiving it:

```bash
msg list                    # the message is there, labelled `reconstruct`
msg act <message-id>        # unwraps your half, completes it, verifies, writes the enc-key file
```

`msg act` re-checks the subject, reads exactly one share-shaped token from the body, and calls
`key-reconstruct` — which opens the envelope with **your private key**, reads the local half from
**this machine**, reconstructs, proves the result (§3), writes `~/.euler/enc-key.json`, and wires
the git filter so the private solutions decrypt in place. The message is dismissed once it
worked: its whole content is now in your enc-key file.

By hand, when a share arrived some other way:

```bash
key-reconstruct <the blob, or a bare 262-hex share>   # reader floor; asks for it if omitted
```

### Granting access off the host

A machine that is not on the host has no local half to complete, and the spool cannot reach it
either. Both ends are commands of their own, and both are `admin`:

```bash
host-authorize <public-key> <email>     # on a machine that holds the master key
host-unlock                             # on the machine being authorized; paste the block
```

`host-authorize` seals the **whole** master key to that public key and mails it, with a block to
copy:

```
----- BEGIN EULER MASTER KEY -----
{
  "verify": "…",
  "<their public key>": "…"
}
----- END EULER MASTER KEY -----
```

The payload is inert to the mail provider, to the operator's own mailbox and to anyone who later
reads either: without the matching private key it is 300-odd bytes of noise. Mail goes through
the loopback relay from the operator's terminal — the egress firewall permits that uid and bars
every per-user one — and when the relay cannot be reached the block is **printed instead**, so a
mail problem never costs a grant.

`host-unlock` takes the block, proves it (unwraps with this machine's private key, `verify` must
decrypt to the known text) and writes the enc-key file. The markers are for the person deciding
what to copy; the reader finds the JSON object inside whatever it is given, so quoting, wrapping
and surrounding prose are all harmless.

This deliberately trades the split's third factor for a channel that arrives. Use it where there
is no host to share a half with — not as the ordinary grant.

---

## 6. Rotation

`key-rekey` mints a new master key, re-encrypts the tracked private files, and **redraws the
local half** against the new key.

Why redraw, given that `key-split` refuses a stale half anyway? Because refusing is the fallback,
not the design. A half left over from before a rotation is not wrong on its face — any point plus
any secret determines a line, so it would still complete, into the **retired** key — and only the
`verify` record lets `key-split` catch it. Redrawing during the rotation means no window exists
in which the file and the key disagree, and the next grant can send immediately instead of being
sent back through the laying phase.

The redraw is *not* part of the re-encryption commit: the share is host state, not repository
content, so it never enters a commit at all.

A rotation also **invalidates every outstanding sent half**, which is the closest thing this
scheme has to revocation: an unclaimed half stops being useful the moment its key is retired.
The same is true of a key mailed by `host-authorize`.

`key-rekey` re-issues the *whole* key to existing holders rather than halves, deliberately: its
messages go out after the re-encrypted tree is published, every holder must sync regardless, and
a rotation that half-fails must not also leave people unable to complete a share.

---

## 7. Security properties, and the limits

**What the mathematics gives you.** A single share is information-theoretically independent of
the master key. Nothing an attacker does to one half tells them anything about the key.

**What the deployment gives you.** The two halves are held by different things — a private key,
and an account on the host:

| an attacker holds | outcome |
| --- | --- |
| the local half, forever | nothing |
| the sealed message, with or without host access | nothing without that private key |
| the sealed message **and** the recipient's private key | nothing without host access |
| all three | the master key — the intended outcome, in the recipient's hands |

The row that matters is the third: a stolen `~/.euler` plus a copy of the spool is enough for an
*issued* key and not for a split one. That is the whole benefit, and it is why the half must not
be published — which it was, while it was tracked in a public repository.

**Off-host grants have two factors, not three**, by construction (§5). `host-authorize` is the
deliberate exception, not a second-best.

**Floors.** `key-split` and `user-authorize` require `maintainer`; `host-authorize` and
`host-unlock` require `admin` — they cross a machine boundary and send a whole key, and the
relay is reachable only from an operator's uid anyway. `key-reconstruct` requires `reader`,
because completing a half you were sent writes nothing but your own file, and the person who
most needs it is by definition the one with the least access.

**Proof of possession, not authority.** Every grant command can only be run by somebody who
currently holds and verifies the master key (`read_master_key` at the top). There is no central
registry of who *may* grant, and therefore none to compromise.

**What is recorded.** An on-host grant writes `public_key` and `key_issued` into the roster: an
act, and its date. Not "has access" — whether they still hold the key is a fact in their own
enc-key file, and a stale `true` would mislead the next rotation. An off-host grant records
nothing, because an off-host machine has no account to record it against.

---

## 8. Tests

[`tests/test_roster.py`](../tests/test_roster.py):

| class | what it pins |
| --- | --- |
| `StoreTests` | every degraded roster state reads as empty rather than raising; `upsert` merges; records are keyed by slug and carry no address; a removed record leaves the registry; **no key material is ever written there** |
| `AuthorizeTests` | a grant records the key and sends a half that completes into the master key; it refuses — sending nothing, dismissing nothing — while the local half is missing or stale; a bare key still needs an identity |
| `HostGrantTests` | the mailed block unlocks the machine it was sealed to; it survives a mail client's quoting and wrapping; a block sealed to another machine is refused with nothing written; an unreachable relay prints the block rather than losing it |

[`tests/test_enc_key.py`](../tests/test_enc_key.py):

| class | what it pins |
| --- | --- |
| `KeySplitTests` | the first run lays the local half and sends nothing; the second sends under the share subject; the message carries **no share in the clear** and does not open with another key; a recipient with no public key is refused before anything is minted; the roster supplies the key when none is passed; every holder gets a different half; the issue is recorded and dated; a half from before a rotation is redrawn rather than completed |
| `KeyReconstructTests` | the two halves make the key and wire the filter; a half sealed to somebody else is refused; a bare share still works by hand; a wrong share is caught by the share file's own `verify` on a machine with no enc-key file; a bad reconstruction leaves a working file alone; a machine with no half says so; shape rejection; the share survives the prose around it |

[`tests/test_messaging.py`](../tests/test_messaging.py) pins the dispatch: a
`Master key share for …` message maps to `reconstruct`, at every rung, and never to `save`.

---

## 9. Files

| file | role |
| --- | --- |
| [`solver/crypto/keys.py`](../solver/crypto/keys.py) | the field arithmetic, the sealing, `key-split`, `key-reconstruct`, `user-authorize`, `host-authorize`, `host-unlock` |
| [`solver/crypto/config.py`](../solver/crypto/config.py) | `share_file` — where the local half lives, and the order it is looked for in |
| [`solver/crypto/ciphers.py`](../solver/crypto/ciphers.py) | `lock` / `unlock` — the X25519 envelope a sent half and a mailed key both ride in |
| [`solver/auth/roster.py`](../solver/auth/roster.py) | the roster: public keys and the operator's dated acts, and no key material |
| [`solver/web/auth/mail.py`](../solver/web/auth/mail.py) | `send_master_key` — the off-host delivery |
| [`solver/web/msg/__init__.py`](../solver/web/msg/__init__.py) | `KEY_SHARE_SUBJECT` and `verb_for`, which make `msg act` on such a message *be* the reconstruction |
| [`solver/web/msg/commands.py`](../solver/web/msg/commands.py) | `_reconstruct` — the receiving half of `msg act` |
