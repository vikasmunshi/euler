# Git Filter Guide — transparent encryption for `solutions/private/`

This guide covers the **transparent git encryption** for files under
`solutions/private/`: how it works, how to set it up, day-to-day use, and how to
prove the files are encrypted at rest. It is implemented in
[`solver/crypto/gitfilter.py`](../solver/crypto/gitfilter.py).

The key material it relies on (your identity and the master key) is described in
[User Guide §7](user-guide.md#7-key-exchange). Encryption is opt-in per file via
`.gitattributes` (only `solutions/private/`).

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

### The master key file

The master key lives in `keys/enc-key.json`, a flat map keyed by **public key**:

```
enc-key.json
├── <public-key-hex>    - the 32-byte master key wrapped for this X25519 public key
│                         (ephemeral X25519 ECDH → HKDF-SHA256 → ChaCha20-Poly1305)
├── … one entry per authorised public key …
└── verify              - MAGIC|nonce|ciphertext: the master key encrypting a fixed
                          known text (Blake's "Auguries of Innocence", opening quatrain)
```

No email is stored anywhere — a key is identified solely by its public-key value.
To use the master key the filter unwraps the current user's entry with the private
key at `~/.euler/id` (PKCS8 PEM, plain/unencrypted; a machine-local `0600` file in
the sibling secrets dir outside the checkout, so its file permissions are its
protection). All of this lives in `solver/crypto/ciphers.py`.

The `verify` field makes the key **self-checking**: loading the master key always
decrypts `verify` and compares it to the known text. A wrong or corrupt key is
rejected rather than used to write garbage. The file is safe to commit — it holds
only wrapped keys and a ciphertext, never a plaintext key.

### Constants

All crypto configuration — file locations **and** wire-format / filter constants —
lives in one place, `solver.crypto.ciphers.config_dict` (`config_dict['magic']`,
`config_dict['filter_name']`, `config_dict['attr_line']`, `config_dict['pkt_max']`,
`config_dict['verify_text']`, …), so the filter and the audit script share a single
source of truth and the crypto package does not depend on `solver.config`.

---

## 3. Setup

You need an X25519 identity with master-key access first. Run `solver user`; if it reports
`✗ cannot encrypt/decrypt`, have an existing user `authorize` your public key (the master key is
created once and committed in `keys/enc-key.json`). See
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
| `key-split <n> <t>` / `key-reconstruct <t>` | Split the master key into `n` shares (any `t` reconstruct) / recover it from `t` shares. |

---

## 6. Multi-user and key rotation

- **Add a user:** they run `solver user` to create their identity and share their
  public key; any existing key holder runs `solver "authorize <public-key-hex>"` to
  wrap the master key to it in `enc-key.json`. Commit the updated file.
- **Rotate the master key:** `solver rekey`. It verifies the current key, generates
  a new one, re-wraps it to all authorised public keys, refreshes `verify`, and
  re-encrypts the tracked private files. Commit the new `enc-key.json` **and** the
  re-encrypted blobs together.

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
| `master key check FAILED` on `install` | No `keys/enc-key.json` yet, no `~/.euler/id`, or your public key has no entry. Run `solver user`, then have an existing user `authorize` your public key (the master key is committed in `keys/enc-key.json`). |
| Checkout/commit of private files aborts | `required = true` and the master key is unavailable. Obtain master-key access (see §6), or you genuinely cannot read these files. |
| Other clones see ciphertext in the working tree | `.gitattributes` was not committed, or the filter was never `install`-ed on that clone. Commit `.gitattributes`; run `solver-gitfilter install`. |
| Spurious "modified" on `status` with no edits | Determinism broke — the master key in use differs from the one a blob was encrypted with (e.g. after a partial rekey). Reconcile the master key, then `git add --renormalize`. |

---
