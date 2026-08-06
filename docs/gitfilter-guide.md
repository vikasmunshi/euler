# Git Filter Guide — transparent encryption for `solutions/private/`

This guide covers the **transparent git encryption** for files under
`solutions/private/`: how it works, how to set it up, day-to-day use, and how to
prove the files are encrypted at rest. It is implemented in
[`solver/crypto/gitfilter.py`](../solver/crypto/gitfilter.py).

The key material it relies on (your identity and the master key) is described in
[User Guide §7](user-guide.md#7-key-exchange). Encryption is opt-in per file via
`.gitattributes` (only `solutions/private/`).

Three companion guides cover the schemes around it: the [Vault Guide](vault-guide.md) for how
your private key rests encrypted, the [Secret Sharing Guide](secret-sharing-guide.md) for the
2-of-2 master-key split (`key-split` / `key-reconstruct`), and the [SRP Guide](srp-guide.md)
for the web login, which shares no key material with any of this.

---

## 1. What it does

Files under `solutions/private/` are stored **encrypted in git** (in the index,
in commits, on the remote) but appear as **plaintext in your working tree**. You
edit and run them normally; git encrypts on the way in and decrypts on the way
out. You can work on many problems at once.

```
   working tree                git object store / remote
   (what you edit)             (what is committed & pushed)
   ┌────────────────┐  add →   ┌──────────────────────────┐
   │ plaintext .py  │ ──clean──│ SLVR…  AES-256-GCM bytes  │
   │                │ ◀─smudge─│                          │
   └────────────────┘ ← checkout└──────────────────────────┘
```

`solutions/public/` is plaintext and tracked normally — only `solutions/private/`
is routed through the filter.

---

## 2. How it works

It is a [git clean/smudge filter](https://git-scm.com/docs/gitattributes#_filter).
A filter must be **deterministic** — the same plaintext must encrypt to
byte-identical ciphertext every time, or git reports spurious modifications on
every `status`/`add`. To achieve that:

- One fixed AES-256 key and one nonce-HMAC key are derived from a **master key**
  via HKDF-SHA256.
- The nonce is `HMAC(plaintext)` — so identical plaintext yields identical
  ciphertext (no churn), while distinct plaintext gets a distinct nonce (no
  GCM nonce reuse under the fixed key). This is the convergent-encryption trick
  `git-crypt` uses.

**Wire format** of an encrypted blob:

```
MAGIC (5 bytes) | nonce (12 bytes) | AES-256-GCM ciphertext+tag
```

`MAGIC` is `b'SLVR\x01'`. Content that does not start with `MAGIC` is passed
through unchanged, so plaintext files committed before the filter existed, and
already-encrypted blobs, are never double-processed.

### Why the filter command carries `-P`

git runs a filter with the working directory at the **top of the worktree**, and a solver
checkout has a `solver/` package sitting right there. Without `-P` (PYTHONSAFEPATH), Python
prepends that cwd to `sys.path`, so `python -m solver.crypto.gitfilter` imports **the clone's
own source** rather than the installed copy in the venv the command names. A collaborator
whose clone is behind then runs an *old* filter against a *current* key file.

The signature to remember: **the shell and the filter disagree about the same clone.** `user`
says the key is available (a console script, sane `sys.path`, current code) while `git-filter`
says UNAVAILABLE (a filter process, shadowed import, stale code).

The flag is written into `.git/config` by `install`. A clone keeps whatever command was
recorded the day it was set up, so **taking a key compares the recorded command with what
`install` would write today** and re-wires when they differ — any change to that command
repairs itself the next time a key is saved.

It hangs off `msg act`, because taking a key is the one act that changes what a machine can
decrypt. A drifted clone therefore waits for its owner's next save; `git-filter install` is
the manual repair.

The re-checkout either does is guarded: local plaintext edits are never clobbered — it says so
and skips, rather than running `rm -f` over somebody's work.

### When the key cannot be reached

The filter answers `status=abort` — the protocol's word for "not this file, and not any after
it" — rather than exiting. What git does with that is `filter.solver-crypt.required`'s
business: **required** (the normal wiring) fails the checkout with the filter's own message,
**not required** falls back to the stored content, so ciphertext lands in the worktree and git
succeeds. That is the state an un-authorized clone is designed to sit in, and it is what
`scripts/ops/reset-user.sh --no-filter` relies on.

Exiting before the handshake instead gives git a filter that dies on startup, reported as
`fatal: the remote end hung up unexpectedly` — a *transport* failure, which `required=false`
cannot soften because there is no filter result to fall back from.

### The master key file

The master key lives in **`~/.euler/enc-key.json`** — machine-local, `0600`, beside the
private key that opens it, and **not in the checkout**. Two records:

```
~/.euler/enc-key.json
├── verify              - MAGIC|nonce|ciphertext: the master key encrypting a fixed
│                         known text (Blake's "Auguries of Innocence", opening quatrain)
└── <your-public-key>   - the 32-byte master key wrapped for it (ephemeral X25519 ECDH
                          → HKDF-SHA256 → ChaCha20-Poly1305)
```

That is the whole file. It holds **your** entry and nobody else's, so there is no attribution
to keep, nothing to purge, and no shared copy to reconcile with.

It used to be tracked: `keys/enc-key.json`, every authorised key, committed and pulled. The
cost was structural. A rotation had to edit that tracked file, `sync.sh` stashes a dirty tree
around the merge and pops it after, and the authorised copy arriving from the other side made
the pop conflict — leaving markers in JSON that every reader takes for "not authorised",
decryption included. A reader could not even repair it: `git-reset` was contributor-floored then (it sits at
`reader` now). It
also needed an attribution map to say whose entries were whose, a purge verb to remove the
stale ones, a machine-local overlay to bridge rotations, and a repair path inside `git-sync`.
All of that was the price of keeping per-machine key material in shared state.

**Distribution is the message spool.** A maintainer's `user-authorize` wraps the master key to
your public key and sends you the payload — the whole of your file — and `msg act` writes it
after checking it unwraps with your private key and passes `verify`. It travels by message for
the same reason the old file could sit in a public repo: without your private key it is inert.

**A rotation needs nobody.** `user --regen` re-wraps the master key to your new public key in
place, because the file is yours alone. Only a machine that *cannot* load the master key —
a first run, or a rotation whose carry failed — files a request.

The `verify` field makes the key **self-checking**: loading the master key always
decrypts `verify` and compares it to the known text. A wrong or corrupt key is
rejected rather than used to write garbage. The file is safe to commit — it holds
only wrapped keys and a ciphertext, never a plaintext key.

### Constants

The wire-format and filter constants — `wire.MAGIC`, `wire.FILTER_NAME`,
`wire.ATTR_LINE`, `wire.PKT_MAX`, `wire.VERIFY_TEXT`, … — live in
[`solver/crypto/wire.py`](../solver/crypto/wire.py), so the filter and the audit script
share a single source of truth. None of them is configurable: each is part of a format
something else already depends on — a blob in git, a file on another machine, a rule in
the tracked `.gitattributes` — so changing one does not adjust behaviour, it makes
existing data unreadable.

Where the *files* are is the configurable part, and it is not kept here: the key
locations are settings like any other, declared in `solver/config/config.py` and
editable in the `[crypto]` section of
[`solver/config/values.conf`](../solver/config/values.conf).

---

## 3. Setup

You need an X25519 identity with master-key access first. Run `solver user`; if it reports
`✗ cannot encrypt/decrypt`, have an existing user `authorize` your public key (the master key is
created once, and held by each user in `~/.euler/enc-key.json`). See
[User Guide §7](user-guide.md#7-key-exchange). Then:

```bash
solver-gitfilter install           # wire git config + .gitattributes, verify the key
```

(`rekey`, `authorize`, `key-split` and `key-reconstruct` are shell commands — they prompt and
print — so they live in `solver`, not in the output-silent `solver-gitfilter` CLI.)

`install` is idempotent and, in order:

1. Verifies the master key against `verify`, exiting non-zero and **wiring nothing** if it
   fails — so a failed install can never leave `required = true` set with no usable key.
2. Registers the filter in the **local** git config:
   ```
   filter.solver-crypt.process = <python> -m solver.crypto.gitfilter process
   filter.solver-crypt.clean   = <python> -m solver.crypto.gitfilter clean
   filter.solver-crypt.smudge  = <python> -m solver.crypto.gitfilter smudge
   filter.solver-crypt.required = true
   ```
3. Ensures `.gitattributes` contains:
   ```
   solutions/private/** filter=solver-crypt -text
   ```

> **`.gitattributes` must be committed.** The repo `.gitignore` ignores dotfiles,
> so `.gitattributes` is git-ignored by default; a `!.gitattributes` negation
> un-ignores it. It works locally even while untracked (git reads the worktree
> copy), but other clones only get the filter once `.gitattributes` is committed.

`required = true` means a filter failure **aborts** the git operation rather than
silently committing plaintext — so a user without the master key cannot check out
or commit private files. That is the intended security boundary.

---

## 4. Daily use

Nothing special — the filter is transparent:

```bash
# create/edit a private solution as plaintext
$EDITOR solutions/private/p0999_s0.py

git add solutions/private/        # clean filter encrypts into the index
git commit                        # encrypted blob is committed
git checkout -- solutions/private # smudge filter decrypts back to plaintext
```

The first `git add` after `install` runs git's **long-running process filter**:
one process encrypts every file in the batch, unwrapping the master key and
building the AES cipher once. (The per-file `clean`/`smudge` actions exist as a
fallback and for manual use.)

---

## 5. CLI reference

The filter plumbing is `solver-gitfilter <action>` (or `python -m solver.crypto.gitfilter <action>`):

| Action | Purpose |
| --- | --- |
| `install` | Verify the master key (exit non-zero, wiring nothing, if it fails), then register the filter in git config + `.gitattributes`. |
| `status` | Print the git-config wiring, `.gitattributes` state, and whether the master key is present and verified. |
| `process` | Git's long-running filter protocol (pkt-line). Invoked by git; not run by hand. |
| `clean` / `smudge` | Single-file encrypt / decrypt over stdin→stdout. Invoked by git as a fallback; usable manually for testing. |

`clean`/`smudge`/`process` write **only** the transformed file content to stdout
(diagnostics go to stderr) — this is why `gitfilter.py` and `ciphers.py` keep their
imports stdout-silent and redirect key-retrieval output to stderr.

Master-key lifecycle is in the interactive `solver` shell (see `solver.crypto.keys`):

| Command | Purpose |
| --- | --- |
| `rekey` | Rotate to a new master key, re-wrap it to **every** authorised public key, and re-encrypt tracked private files (`git add --renormalize`). Requires the current key to verify first. |
| `authorize <public-key-hex>` | Wrap the current master key to another public key (add a user). |
| `key-split <identity> [<public-key>]` | Send someone half the master key, sealed to their public key; the other half is `/etc/euler/share.json` on the host. The first run (or the first after a rotation) writes that half and stops. |
| `key-reconstruct <share>` | Unwrap the half you were sent, complete it from the repository, prove the result, and store it. What `msg act` runs on a `key-split` message. |

---

## 6. Multi-user and key rotation

- **Add a user:** they run `solver user`, which creates their identity and files a key
  request over the message spool. A maintainer works it with `solver "authorize <message-id>"`
  — the key and the requester come from the thread. That records their public key in the
  roster (`/etc/euler/roster/users.json`) and delivers **half** the master key, sealed to that
  key; the other half is `/etc/euler/share.json`, which their instance on this host already
  reads. They run `msg act <id>`, and their private solutions decrypt in place.
- **Lay the host's half:** `solver "key-split"` (maintainer), once per host. With no half yet
  — or one from before a rotation — it writes `/etc/euler/share.json` and **stops**;
  `user-authorize` refuses until it is there. It is never committed: a share published in a
  public repository is no second factor at all.
- **Authorize a machine that is not on this host:** `solver "host-authorize <public-key>
  <email>"` (admin). There is no shared half to complete off the host, so this mails the whole
  master key sealed to that machine's public key, and the far end runs `host-unlock` and pastes
  the block. Two factors rather than three, deliberately — see the
  [Secret Sharing Guide](secret-sharing-guide.md).
- **Rotate your own key:** `solver "user --regen"`. It carries the master key to the new key
  itself; nobody else is involved, and nothing is published.
- **Rotate the master key:** `solver rekey` (admin). It verifies the current key, generates a
  new one, writes yours, re-issues it by message to every public key in the roster
  (a grant records it there), and re-encrypts the tracked private files — redrawing the
  host's share along with them, so `key-split` never completes a half against a retired
  key. Commit the re-encrypted blobs. An account with no public key in the roster **loses
  access at that rotation** and is named before you confirm — sometimes the intent, never a
  surprise.

> A rekey changes every encrypted blob (the derived keys change). Make sure all
> private files are checked out (plaintext present) before rotating, then commit
> the re-encrypted result in one go.

---

## 7. Verifying encryption at rest

The working-tree copy is always plaintext, so `cat`-ing a file proves nothing.
To see what git actually stores, read the **raw blob** (no smudge filter):

```bash
git cat-file -p :solutions/private/p0999_s0.py | head -c 5 | xxd   # → SLVR
git cat-file -p HEAD:solutions/private/p0999_s0.py | xxd | head    # magic + noise
```

`git cat-file -p` and `git show :path` read the object store directly (raw
ciphertext). Anything that touches the **working tree** — `cat`, a checkout, or
`git cat-file --filters` — re-applies the smudge filter and hands you plaintext.

### `scripts/git/audit.sh`

Audits what git actually stores across the **whole tracked tree**, in two
independent checks:

- **encryption at rest** — every tracked file under `solutions/private/` has the
  `MAGIC` header, read straight from its stored blob;
- **compiled binaries** — no tracked file *anywhere* begins with the ELF magic
  (the `p<NNNN>_s<K>_c` runner executables are gitignored build artifacts and must
  never enter git).

```bash
make audit                       # counts only — the periodic full sweep
scripts/git/audit.sh             # per-file report + summary
scripts/git/audit.sh --summary   # counts only
```

Both checks run even if the first fails, and the script exits non-zero if either
found something, which makes it a gate. Offenders are always listed by path;
`--summary` only suppresses the per-file lines for the files that pass (there are
thousands, and the sweep takes ~25s).

This whole-tree sweep **complements** the git hooks rather than being called by
them. Both hooks carry their own inlined equivalents of these checks —
self-contained, so the gates survive this script being changed or removed — and
both scope them to the blobs at hand: pre-commit audits the **staged** blobs
(`scripts/setup/hooks/pre-commit.template`), pre-push audits the blobs **the push
would add to the remote** (`scripts/setup/hooks/pre-push.template`, checks 1 and
2). That keeps every commit and push fast, but it means neither hook re-examines
history that is already on the remote. `make audit` is what covers that: run it
periodically to catch a blob committed before the hooks (or the `.gitattributes`
filter wiring) were in place.

---

## 8. Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `git add` hangs | A stale `process` filter or `.git/index.lock` from an interrupted run. Kill leftover `gitfilter process` procs and remove `.git/index.lock`. |
| `master key check FAILED` on `install` | No `~/.euler/enc-key.json` yet, no `~/.euler/id`, or the file holds a key that is not yours. Run `solver user` — it files a request — then `msg act <id>` when a maintainer issues it. |
| Checkout/commit of private files aborts | `required = true` and the master key is unavailable. Obtain master-key access (see §6), or you genuinely cannot read these files. |
| Other clones see ciphertext in the working tree | `.gitattributes` was not committed, or the filter was never `install`-ed on that clone. Commit `.gitattributes`; run `solver-gitfilter install`. |
| Spurious "modified" on `status` with no edits | Determinism broke — the master key in use differs from the one a blob was encrypted with (e.g. after a partial rekey). Reconcile the master key, then `git add --renormalize`. |

---
