# Git Filter Guide — transparent encryption for `solutions/private/`

This guide covers the **transparent git encryption** for files under
`solutions/private/`: how it works, how to set it up, day-to-day use, and how to
prove the files are encrypted at rest. It is implemented in
[`solver/crypto/gitfilter.py`](../solver/crypto/gitfilter.py).

If you are looking for the older pool-based scheme that encrypts problems #101+
in place (`*.enc` files, `keys/keys.json`), see [User Guide §7](user-guide.md#7-key-exchange).
The two are independent; this one is opt-in per file via `.gitattributes`.

---

## 1. What it does

Files under `solutions/private/` are stored **encrypted in git** (in the index,
in commits, on the remote) but appear as **plaintext in your working tree**. You
edit and run them normally; git encrypts on the way in and decrypts on the way
out. There is no `init`/`stack`/`reset` step and no workspace lock — you can work
on many problems at once.

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

The master key lives in its own file, `keys/master_key.json`
(`config.master_key_file`), **separate** from `keys/keys.json`:

```
master_key.json
├── users/              - one entry per authorised user
│   └── <email>
│       ├── public_key  - user's X25519 public key (hex)
│       └── master_key  - the 32-byte master key wrapped for this user
│                         (ephemeral X25519 ECDH → HKDF-SHA256 → ChaCha20-Poly1305)
└── verify              - MAGIC|nonce|ciphertext: the master key encrypting a fixed
                          known text (Blake's "Auguries of Innocence", opening quatrain)
```

Multi-user access is free: the master key is wrapped per user with the same
X25519 scheme as `keys.json` (`solver/crypto/asymmetrical.py`). To use it, the
filter unwraps the current user's copy with the private key at `~/.ssh/id_solver`.

The `verify` field makes the key **self-checking**: loading the master key always
decrypts `verify` and compares it to the known text. A wrong or corrupt key is
rejected rather than used to write garbage. The file is safe to commit — it holds
only wrapped keys and a ciphertext, never a plaintext key.

### Constants

All wire-format and filter constants live on `config` (`config.gitfilter_magic`,
`config.gitfilter_name`, `config.gitfilter_attr_line`, `config.gitfilter_pkt_max`,
`config.gitfilter_verify_text`, …) so the filter and the audit script share a
single source of truth.

---

## 3. Setup

You need an X25519 identity first (`~/.ssh/id_solver` — run `solver user` if you
have not already; see [User Guide §7](user-guide.md#7-key-exchange)). Then:

```bash
solver-gitfilter generate-master   # create keys/master_key.json (once per repo)
solver-gitfilter install           # wire git config + .gitattributes, verify the key
```

`install` is idempotent and:

1. Registers the filter in the **local** git config:
   ```
   filter.solver-crypt.process = <python> -m solver.crypto.gitfilter process
   filter.solver-crypt.clean   = <python> -m solver.crypto.gitfilter clean
   filter.solver-crypt.smudge  = <python> -m solver.crypto.gitfilter smudge
   filter.solver-crypt.required = true
   ```
2. Ensures `.gitattributes` contains:
   ```
   solutions/private/** filter=solver-crypt -text
   ```
3. Verifies the master key against `verify`, exiting non-zero if it fails.

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

Invoke as `solver-gitfilter <action>` or `python -m solver.crypto.gitfilter <action>`.

| Action | Purpose |
| --- | --- |
| `generate-master` | Create `keys/master_key.json`: fresh master key, wrapped to you, plus the `verify` ciphertext. Pass `--force` to overwrite an existing file. |
| `install` | Register the filter in git config + `.gitattributes`, then verify the master key or exit non-zero. |
| `status` | Print the git-config wiring, `.gitattributes` state, and whether the master key is present and verified. |
| `rekey-master` | Rotate to a new master key, re-wrap it to **every** stored user, and re-encrypt tracked private files (`git add --renormalize`). Requires the current key to verify first. |
| `process` | Git's long-running filter protocol (pkt-line). Invoked by git; not run by hand. |
| `clean` / `smudge` | Single-file encrypt / decrypt over stdin→stdout. Invoked by git as a fallback; usable manually for testing. |

`clean`/`smudge`/`process` write **only** the transformed file content to stdout
(diagnostics go to stderr) — this is why `gitfilter.py` keeps its imports
stdout-silent and redirects key-retrieval output to stderr.

---

## 6. Multi-user and key rotation

- **Add a user:** they run `solver user` to create their identity, then their
  `master_key` entry must be added to `master_key.json` wrapped to their public
  key (admin task — re-wrap the current master key to the new user's
  `public_key`). Commit the updated file.
- **Rotate the master key:** `solver-gitfilter rekey-master`. It verifies the
  current key, generates a new one, re-wraps it to all stored users, refreshes
  `verify`, and re-encrypts the tracked private files. Commit the new
  `master_key.json` **and** the re-encrypted blobs together.

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

### `scripts/git/audit-private.sh`

Audits **every** tracked file under `solutions/private/` by reading its stored
blob and checking for the `MAGIC` header:

```bash
scripts/git/audit-private.sh             # per-file report + summary
scripts/git/audit-private.sh --summary   # counts only
```

It exits non-zero if any tracked private file is stored as plaintext (a file that
slipped past the filter), which makes it a gate. It is **wired into the pre-push
hook** (`scripts/setup/hooks/pre-push.template`, check 3): a push is blocked if
any private file would be pushed in the clear.

---

## 8. Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `git add` hangs | A stale `process` filter or `.git/index.lock` from an interrupted run. Kill leftover `gitfilter process` procs and remove `.git/index.lock`. |
| `master key check FAILED` on `install` | No `keys/master_key.json` yet, or the current user has no entry / a wrong private key. Run `generate-master`, or have an admin wrap the master key to your `public_key`. |
| Checkout/commit of private files aborts | `required = true` and the master key is unavailable. Obtain master-key access (see §6), or you genuinely cannot read these files. |
| Other clones see ciphertext in the working tree | `.gitattributes` was not committed, or the filter was never `install`-ed on that clone. Commit `.gitattributes`; run `solver-gitfilter install`. |
| Spurious "modified" on `status` with no edits | Determinism broke — the master key in use differs from the one a blob was encrypted with (e.g. after a partial rekey). Reconcile the master key, then `git add --renormalize`. |

---
