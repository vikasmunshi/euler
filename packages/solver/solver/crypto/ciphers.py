#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Ciphers: read keys from disk and lock/unlock, encrypt/decrypt with no user interaction.

This is the non-interactive heart of `solver.crypto`. File locations and git-filter wire-format
file locations come from `solver.config` and the wire-format constants from `solver.crypto.wire` (the
import `solver.config`). On top of that, this module owns:

- the asymmetric primitives -- load the plain (unencrypted) X25519 private key from `~/.euler/id`
  (a machine-local `0600` file outside the repo), and `lock`/`unlock` (wrap/unwrap) a secret to an
  X25519 public key via ephemeral ECDH -> HKDF-SHA256 -> ChaCha20-Poly1305.
- the master (symmetrical) key -- `read_master_key` unwraps this machine's entry from
  `~/.euler/enc-key.json` (two records: `verify`, and the master key wrapped to this holder's
  public key) and proves it correct by decrypting `verify` before returning it. `enc_key_payload`
  builds that pair for somebody else -- the unit `user-authorize` sends and `msg act` writes.
- deterministic blob encryption -- the convergent-encryption core used by the git filter: one fixed
  AES-256 key + a content-derived nonce (`HMAC(plaintext)`), so identical plaintext always yields
  byte-identical ciphertext (no spurious git diffs).

All creation, persistence, rotation, sharing and the shell commands live in `solver.crypto.keys`
(which is interactive and imports this module). The git filter (`solver.crypto.gitfilter`) imports
only this module. Both of those callers run in contexts where stdout carries file content, so this
module's hard contract is: **importing it, and everything it imports, emits nothing on stdout.** It
imports only the standard library, `cryptography`, `solver.config` and `solver.crypto.wire`; keep it that way.
Verified: `python -c "import solver.crypto.ciphers"` writes 0 bytes to stdout.
"""
from __future__ import annotations

__all__ = [
    'build_cipher',
    'decrypt_blob',
    'decrypt_blob_with',
    'encrypt_blob',
    'encrypt_blob_with',
    'enc_key_payload',
    'is_encrypted',
    'load_private_key',
    'lock',
    'public_key_hex',
    'read_enc_key_file',
    'read_master_key',
    'unlock',
    'verify_master_key',
]

from functools import lru_cache
from hashlib import sha256
from hmac import new as hmac_new
from json import loads
from pathlib import Path
from typing import Any, cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (Encoding, PublicFormat, load_pem_private_key)

from solver.config import config
from solver.crypto import wire
from solver.crypto.vault import decrypt_secret, is_vault_encrypted, session_vault_key


# ==================================================================================================================== #
#                                               asymmetric key load + wrap/unwrap
# ==================================================================================================================== #
def public_key_hex(public_key: X25519PublicKey) -> str:
    """Return the raw 32-byte X25519 public key as a lowercase hex string (its identity in the enc-key file)."""
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
    key_file: Path = config.private_key_file
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
    """Read and parse this machine's enc-key file; FileNotFoundError when there is none."""
    return cast(dict[str, Any], loads(config.enc_key_file.read_text()))


def verify_master_key(data: dict[str, Any], master_key: bytes) -> bool:
    """Return True if `master_key` decrypts the stored `verify` ciphertext back to the known plaintext."""
    try:
        blob = bytes.fromhex(str(data[wire.ENC_KEY_VERIFY]))
        return decrypt_blob(blob, master_key) == bytes(wire.VERIFY_TEXT)
    except (InvalidTag, ValueError, KeyError, TypeError):
        return False


@lru_cache(maxsize=None)
def read_master_key() -> bytes:
    """Unlock this machine's master key and prove it correct.

    One file, two records: `verify`, and this holder's own wrapped key. Read the entry that
    matches the private key, unwrap it, and check it against `verify` before returning —
    the same proof as ever, on a file that is now nobody's but this machine's.

    There is no second source and no fallback. The tracked, shared file this replaced needed
    both (an overlay for the window between rotating and being re-authorised, a repair for
    when git mangled it); a file that only this machine writes has no such windows.

    Returns:
        The verified 32-byte master key.

    Raises:
        FileNotFoundError: If the private key or the enc-key file is missing.
        KeyError:          If the file holds no entry for this public key.
        ValueError:        If the key cannot be unwrapped or fails verification.
    Note: Used in solver.crypto.gitfilter; must not emit anything to stdout.
    """
    private_key: X25519PrivateKey = load_private_key()
    data: dict[str, Any] = read_enc_key_file()
    my_public: str = public_key_hex(private_key.public_key())
    if my_public not in data:
        raise KeyError(f'public key {my_public} has no entry in {config.enc_key_file}')
    try:
        master_key: bytes = unlock(private_key, str(data[my_public]))
    except InvalidTag as exc:
        raise ValueError('master key could not be unwrapped with this private key') from exc
    if not verify_master_key(data, master_key):
        raise ValueError('master key failed verification against the stored ciphertext')
    return master_key


def enc_key_payload(public_key: X25519PublicKey, master_key: bytes) -> dict[str, str]:
    """The whole file, for one holder: `{verify, <their-public-key>: <wrapped master key>}`.

    What `user-authorize` sends and `msg act` writes — the unit of key distribution now that
    there is no shared file to append to. Wrapped to *their* public key, so it is theirs alone
    to open, and it travels through the message spool for the same reason the old file could
    sit in a public repo: without the matching private key it is inert.
    """
    return {wire.ENC_KEY_VERIFY: encrypt_blob(wire.VERIFY_TEXT, master_key).hex(),
            public_key_hex(public_key): lock(public_key, master_key)}


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
    magic: bytes = wire.MAGIC
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
    magic: bytes = wire.MAGIC
    nonce: bytes = hmac_new(mac_key, plaintext, sha256).digest()[:wire.NONCE_LEN]
    return magic + nonce + cipher.encrypt(nonce, plaintext, None)


def decrypt_blob_with(blob: bytes, cipher: AESGCM) -> bytes:
    """Decrypt with a prebuilt cipher; pass-through for content without MAGIC."""
    if not is_encrypted(blob):
        return blob
    return cipher.decrypt(blob[len(wire.MAGIC):wire.HEADER_LEN],
                          blob[wire.HEADER_LEN:], None)


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
