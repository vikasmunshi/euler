#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Ciphers: read keys from disk and lock/unlock, encrypt/decrypt with no user interaction.

This is the non-interactive heart of `solver.crypto`. File locations and git-filter wire-format
constants come from the `config` TypedDict in `solver.crypto.config` (the crypto package does **not**
import `solver.config`). On top of that, this module owns:

- the asymmetric primitives -- load the plain (unencrypted) X25519 private key from `~/.euler/id`
  (a machine-local `0600` file outside the repo), and `lock`/`unlock` (wrap/unwrap) a secret to an
  X25519 public key via ephemeral ECDH -> HKDF-SHA256 -> ChaCha20-Poly1305.
- the master (symmetrical) key -- `read_master_key` unwraps the current user's entry from
  `keys/enc-key.json` (a `{<public-key-hex>: <locked-master-key-hex>}` map plus the reserved
  `verify` and `owners` entries) and proves it correct by decrypting `verify` before returning it.
  `authorised_keys` / `key_owners` are the readers for those two: which keys may decrypt, and
  whose key each one is (attribution for `users purge` -- never consulted by the decrypt path).
- deterministic blob encryption -- the convergent-encryption core used by the git filter: one fixed
  AES-256 key + a content-derived nonce (`HMAC(plaintext)`), so identical plaintext always yields
  byte-identical ciphertext (no spurious git diffs).

All creation, persistence, rotation, sharing and the shell commands live in `solver.crypto.keys`
(which is interactive and imports this module). The git filter (`solver.crypto.gitfilter`) imports
only this module. Both of those callers run in contexts where stdout carries file content, so this
module's hard contract is: **importing it, and everything it imports, emits nothing on stdout.** It
imports only the standard library, `cryptography`, and `solver.crypto.config`; keep it that way.
Verified: `python -c "import solver.crypto.ciphers"` writes 0 bytes to stdout.
"""
from __future__ import annotations

__all__ = [
    'authorised_keys',
    'build_cipher',
    'clear_local_enc_key',
    'current_key_slugs',
    'decrypt_blob',
    'decrypt_blob_with',
    'encrypt_blob',
    'encrypt_blob_with',
    'is_encrypted',
    'key_owners',
    'load_private_key',
    'lock',
    'prune_local_enc_key',
    'public_key_hex',
    'read_enc_key_file',
    'read_local_enc_key',
    'read_master_key',
    'unlock',
    'verify_master_key',
    'write_local_enc_key',
]

from functools import lru_cache
from hashlib import sha256
from hmac import new as hmac_new
from json import dumps, loads
from pathlib import Path
from typing import Any, cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (Encoding, PublicFormat, load_pem_private_key)

from solver.crypto.config import config
from solver.crypto.vault import decrypt_secret, is_vault_encrypted, session_vault_key


# ==================================================================================================================== #
#                                               asymmetric key load + wrap/unwrap
# ==================================================================================================================== #
def public_key_hex(public_key: X25519PublicKey) -> str:
    """Return the raw 32-byte X25519 public key as a lowercase hex string (its identity in enc-key.json)."""
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


@lru_cache(maxsize=None)
def load_private_key() -> X25519PrivateKey:
    """Load the X25519 private key from disk (no interaction).

    The key file is machine-local, `0600`, and outside the repo (`~/.euler/id`). It is stored either
    plain (file permissions are its protection) or -- once a per-user vault is initialised -- encrypted
    under the session vault key (`solver.crypto.vault`); this loader transparently decrypts the vault
    form, so callers are unaffected.

    Raises:
        FileNotFoundError: If the private key file is missing.
        ValueError:        If the key file is malformed, or is vault-encrypted while the vault is locked.
    Note: Used in solver.crypto.gitfilter; must not emit anything to stdout.
    """
    key_file: Path = config['private_key_file']
    if not key_file.exists():
        raise FileNotFoundError(f'private key {key_file} not found; run `solver user` to create one')
    raw: bytes = key_file.read_bytes()
    if is_vault_encrypted(raw):
        vault_key: bytes | None = session_vault_key()
        if vault_key is None:
            raise ValueError(f'{key_file} is vault-encrypted but the vault is locked; unlock it first')
        try:
            raw = decrypt_secret(vault_key, raw)
        except InvalidTag:
            # A stale/foreign session key must surface as the SAME failure type as a
            # locked vault — "unreadable", never "absent" — so no caller can mistake a
            # vault failure for a missing identity and mint a new key over the real one.
            raise ValueError(f'{key_file} is vault-encrypted but the session vault key does not '
                             'decrypt it (stale session key, or a foreign vault?)') from None
    key = load_pem_private_key(raw, password=None)
    if not isinstance(key, X25519PrivateKey):
        raise ValueError(f'{key_file} does not contain an X25519 private key')
    return key


def lock(public_key: X25519PublicKey, secret: bytes) -> str:
    """Wrap `secret` so only the holder of `public_key`'s private key can unwrap it.

    Ephemeral X25519 ECDH -> HKDF-SHA256 -> ChaCha20-Poly1305. The ephemeral public key is prepended
    to the ciphertext; the nonce is fixed because a fresh ephemeral key is generated on every call.

    Returns:
        Hex string of (32-byte ephemeral public key | ChaCha20-Poly1305 ciphertext).
    """
    ephemeral: X25519PrivateKey = x25519.X25519PrivateKey.generate()
    shared_secret: bytes = ephemeral.exchange(public_key)
    derived: bytes = HKDF(SHA256(), 32, None, b'key-encryption').derive(shared_secret)
    ciphertext: bytes = ChaCha20Poly1305(derived).encrypt(b'\x00' * 12, secret, None)
    ephemeral_public: bytes = ephemeral.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return (ephemeral_public + ciphertext).hex()


def unlock(private_key: X25519PrivateKey, locked: str) -> bytes:
    """Unwrap a secret produced by `lock` using `private_key`.

    Raises:
        cryptography.exceptions.InvalidTag: If the wrong private key is used or the blob is corrupt.
    Note: Used in solver.crypto.gitfilter; must not emit anything to stdout.
    """
    raw: bytes = bytes.fromhex(locked)
    ephemeral_public: X25519PublicKey = x25519.X25519PublicKey.from_public_bytes(raw[:32])
    shared_secret: bytes = private_key.exchange(ephemeral_public)
    derived: bytes = HKDF(SHA256(), 32, None, b'key-encryption').derive(shared_secret)
    return ChaCha20Poly1305(derived).decrypt(b'\x00' * 12, raw[32:], None)


# ==================================================================================================================== #
#                                               master (symmetrical) key
# ==================================================================================================================== #
def read_enc_key_file() -> dict[str, Any]:
    """Read and parse keys/enc-key.json; raises FileNotFoundError if it has not been generated."""
    return cast(dict[str, Any], loads(config['enc_key_file'].read_text()))


def authorised_keys(data: dict[str, Any]) -> list[str]:
    """The public keys the file authorises — every entry that is not a reserved one.

    The one place that knows which entries are keys and which are bookkeeping. Callers
    that need "who may decrypt" ask here rather than each filtering out `verify` (and now
    `owners`) for themselves — the bug that shape invites is a new reserved entry being
    re-wrapped as if it were somebody's public key.
    """
    reserved = {config['enc_key_verify'], config['enc_key_owners']}
    return [key for key in data if key not in reserved]


def key_owners(data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """The attribution map: ``{<slug>: {key, since, by}}``, empty when absent.

    **Keyed by slug, not by public key**, and that is the whole model: a collaborator has
    exactly one authorised key at any moment, so authorising a new one *replaces* the
    record and the key it named stops being anybody's. Keyed the other way the file grew a
    second live entry per rotation and both read as current — which is how one
    collaborator ended up with two "active" keys and `users purge` found nothing to do.

    **Attribution, never authority.** Nothing in the decrypt path consults this: a key with
    no owner still unwraps. It exists so an admin can ask the only question that matters
    for purging — *is this key still somebody's?* — which the file could not answer at all
    before, and answered wrongly while it was keyed by key.

    One shape, not two: a record without a ``key`` is ignored. The file was migrated when
    this became the shape, so nothing in the wild carries the older key-keyed form, and
    keeping a reader for it would mean keeping a second definition of "whose key is this"
    alive to drift against the first.
    """
    owners = data.get(config['enc_key_owners'])
    if not isinstance(owners, dict):
        return {}
    return {str(slug): {str(field): str(value) for field, value in record.items()}
            for slug, record in owners.items()
            if isinstance(record, dict) and record.get('key')}


def current_key_slugs(data: dict[str, Any]) -> dict[str, str]:
    """Invert :func:`key_owners` — ``{<public-key-hex>: <slug>}`` for the *current* keys.

    Every authorised key absent from this map is an **orphan**: superseded by its owner's
    later key, left behind by a removed account, or never attributed at all. The three are
    one thing — a key that is nobody's — and `users purge` treats them alike.
    """
    return {record['key']: slug for slug, record in key_owners(data).items()}


def read_local_enc_key() -> dict[str, str]:
    """The machine-local overlay: ``{<public-key-hex>: <wrapped master key>}``, or ``{}``.

    Exactly one entry — this user's own key — and it exists only in the window between
    rotating a key and an authorised ``enc-key.json`` arriving by ``git-sync``. Keyed by
    public key rather than holding a bare string so a *stale* overlay (written for a key
    since rotated away) simply does not match and is ignored, instead of being fed to an
    unwrap that would fail further downstream.

    Unreadable or malformed reads as absent: this is a stopgap, and a broken one must
    degrade to "no access yet", never to an exception on the git filter's path.
    """
    try:
        loaded = loads(config['enc_key_local_file'].read_text())
    except (OSError, ValueError):
        return {}
    return {str(k): str(v) for k, v in loaded.items()} if isinstance(loaded, dict) else {}


def write_local_enc_key(public_key: str, wrapped: str) -> None:
    """Replace the overlay with the single entry *public_key* → *wrapped* (``0600``).

    Replace, never merge: the file's whole purpose is "the one key this machine holds that
    the shared file does not authorise yet", so a second rotation supersedes the first
    rather than accumulating keys nobody will ever purge.

    Lives here rather than with the other writers in :mod:`solver.crypto.keys` because the
    reader and the delete are here — the overlay's three operations belong together, and
    this module's contract is *no stdout*, not *no writes*.
    """
    target: Path = config['enc_key_local_file']
    target.parent.mkdir(parents=True, exist_ok=True)
    target.parent.chmod(0o700)
    target.write_text(dumps({public_key: wrapped}, indent=2))
    target.chmod(0o600)


def clear_local_enc_key() -> None:
    """Delete the overlay; best-effort, and silent about a file that was never there."""
    try:
        config['enc_key_local_file'].unlink(missing_ok=True)
    except OSError:
        pass        # a read-only secrets dir must not take decryption down with it


def prune_local_enc_key() -> None:
    """Drop the overlay once the shared file authorises this key — from a settled tree only.

    The counterpart to :func:`read_master_key` not doing this itself. Call it where the
    working tree is known to be at rest — after a *completed* ``git-sync``, or from ``user``
    — never from the decrypt path, which also runs inside the git filter mid-merge where
    the tracked file is a state git is still in the middle of writing.

    Silent and best-effort throughout: an unreadable identity or an unparseable tracked
    file simply means "cannot tell yet", which is a reason to keep the fallback, never to
    fail the command that called this in passing.
    """
    try:
        my_public = public_key_hex(load_private_key().public_key())
        if my_public in read_enc_key_file():
            clear_local_enc_key()
    except (FileNotFoundError, ValueError, OSError):
        return


def verify_master_key(data: dict[str, Any], master_key: bytes) -> bool:
    """Return True if `master_key` decrypts the stored `verify` ciphertext back to the known plaintext."""
    try:
        blob = bytes.fromhex(str(data[config['enc_key_verify']]))
        return decrypt_blob(blob, master_key) == bytes(config['verify_text'])
    except (InvalidTag, ValueError, KeyError, TypeError):
        return False


@lru_cache(maxsize=None)
def read_master_key() -> bytes:
    """Unlock the current user's master key and prove it correct.

    Two sources, in this order — the shared file always wins:

    1. **keys/enc-key.json**, the authorised grant list, whenever it names this public key.
    2. **the machine-local overlay**, when it does not — the window between rotating a key
       and a maintainer's ``user-authorize`` reaching this clone by ``git-sync``.

    **This read never deletes the overlay**, even though a tracked hit means the stopgap has
    been superseded. It runs inside the git filter, and mid-merge the tracked file is
    *transient*: git writes the incoming ``keys/enc-key.json`` into the worktree while it
    checks out ``solutions/private/**``, so the filter sees a file that names this key — and
    if the merge then fails and ``sync.sh`` rolls it back, the worktree reverts to the copy
    that does not, with the fallback already deleted. The user ends up worse off than before
    they synced, which is how this was found. Pruning happens at points that see a
    *settled* tree instead (:func:`prune_local_enc_key`).

    Neither present is simply no access. The ``verify`` check is unchanged either way: it
    reads the *shared* file's ciphertext, so a master key reached through the overlay is
    held to exactly the same proof as one reached normally.

    Returns:
        The verified 32-byte master key.

    Raises:
        FileNotFoundError: If the private key, password, or enc-key file is missing.
        KeyError:          If the current user's public key is in neither source.
        ValueError:        If the key cannot be unwrapped or fails verification.
    Note: Used in solver.crypto.gitfilter; must not emit anything to stdout.
    """
    private_key: X25519PrivateKey = load_private_key()
    data: dict[str, Any] = read_enc_key_file()
    my_public: str = public_key_hex(private_key.public_key())
    if my_public in data:
        wrapped = str(data[my_public])
    elif (local := read_local_enc_key().get(my_public)) is not None:
        wrapped = local
    else:
        raise KeyError(f'public key {my_public} has no entry in {config["enc_key_file"]}')
    try:
        master_key: bytes = unlock(private_key, wrapped)
    except InvalidTag as exc:
        raise ValueError('master key could not be unwrapped with this private key') from exc
    if not verify_master_key(data, master_key):
        raise ValueError('master key failed verification against the stored ciphertext')
    return master_key


# ==================================================================================================================== #
#                                               deterministic blob encryption
# ==================================================================================================================== #
def _derive_keys(master_key: bytes) -> tuple[bytes, bytes]:
    """Derive (encryption_key, nonce_hmac_key) from the master key via HKDF-SHA256.

    Two independent 32-byte keys with distinct `info` labels so the value seeding the deterministic
    nonce can never coincide with the AES key.
    """
    enc_key: bytes = HKDF(SHA256(), 32, None, b'solver-git-filter-enc-v1').derive(master_key)
    mac_key: bytes = HKDF(SHA256(), 32, None, b'solver-git-filter-nonce-v1').derive(master_key)
    return enc_key, mac_key


def is_encrypted(blob: bytes) -> bool:
    """Return True if blob carries the filter's MAGIC header (i.e. is already ciphertext)."""
    magic: bytes = config['magic']
    return blob[:len(magic)] == magic


def build_cipher(master_key: bytes) -> tuple[AESGCM, bytes]:
    """Build the (AES-GCM cipher, nonce-HMAC key) pair once for reuse across many blobs (the hot path)."""
    enc_key, mac_key = _derive_keys(master_key)
    return AESGCM(enc_key), mac_key


def encrypt_blob_with(plaintext: bytes, cipher: AESGCM, mac_key: bytes) -> bytes:
    """Encrypt with a prebuilt cipher; idempotent on already-encrypted input.

    Nonce = `HMAC(plaintext)` so identical plaintext yields identical ciphertext (no spurious diffs)
    while distinct plaintext gets a distinct nonce, avoiding GCM nonce reuse under the fixed key.
    """
    if is_encrypted(plaintext):
        return plaintext
    magic: bytes = config['magic']
    nonce: bytes = hmac_new(mac_key, plaintext, sha256).digest()[:config['nonce_len']]
    return magic + nonce + cipher.encrypt(nonce, plaintext, None)


def decrypt_blob_with(blob: bytes, cipher: AESGCM) -> bytes:
    """Decrypt with a prebuilt cipher; pass-through for content without MAGIC."""
    if not is_encrypted(blob):
        return blob
    return cipher.decrypt(blob[len(config['magic']):config['header_len']],
                          blob[config['header_len']:], None)


def encrypt_blob(plaintext: bytes, master_key: bytes) -> bytes:
    """Encrypt plaintext deterministically for storage in git (one-shot; derives keys per call)."""
    cipher, mac_key = build_cipher(master_key)
    return encrypt_blob_with(plaintext, cipher, mac_key)


def decrypt_blob(blob: bytes, master_key: bytes) -> bytes:
    """Decrypt a blob produced by encrypt_blob (one-shot; derives keys per call).

    Raises:
        cryptography.exceptions.InvalidTag: If the blob is corrupt or the wrong key is used.
    """
    cipher, _ = build_cipher(master_key)
    return decrypt_blob_with(blob, cipher)
