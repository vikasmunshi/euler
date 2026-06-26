#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Ciphers: read keys from disk and lock/unlock, encrypt/decrypt with no user interaction.

This is the non-interactive heart of `solver.crypto`. File locations and git-filter wire-format
constants come from the `config` TypedDict in `solver.crypto.config` (the crypto package does **not**
import `solver.config`). On top of that, this module owns:

- the asymmetric primitives -- load the password-protected X25519 private key from `~/.solver/id`
  (the password is read from `keys/.user-pass`), and `lock`/`unlock` (wrap/unwrap) a secret to an
  X25519 public key via ephemeral ECDH -> HKDF-SHA256 -> ChaCha20-Poly1305.
- the master (symmetrical) key -- `read_master_key` unwraps the current user's entry from
  `keys/enc-key.json` (a `{<public-key-hex>: <locked-master-key-hex>}` map plus a `verify` entry)
  and proves it correct by decrypting `verify` before returning it.
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
    'build_cipher',
    'decrypt_blob',
    'decrypt_blob_with',
    'encrypt_blob',
    'encrypt_blob_with',
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
from typing import cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (Encoding, PublicFormat, load_pem_private_key)

from solver.crypto.config import config


# ==================================================================================================================== #
#                                               asymmetric key load + wrap/unwrap
# ==================================================================================================================== #
def public_key_hex(public_key: X25519PublicKey) -> str:
    """Return the raw 32-byte X25519 public key as a lowercase hex string (its identity in enc-key.json)."""
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


@lru_cache(maxsize=None)
def load_private_key() -> X25519PrivateKey:
    """Load the password-protected X25519 private key from disk (no interaction; password read from file).

    Raises:
        FileNotFoundError: If the private key file or the password file is missing.
        ValueError:        If the password is wrong or the key file is malformed.
    Note: Used in solver.crypto.gitfilter; must not emit anything to stdout.
    """
    key_file: Path = config['private_key_file']
    pass_file: Path = config['user_pass_file']
    if not key_file.exists():
        raise FileNotFoundError(f'private key {key_file} not found; run `solver user` to create one')
    if not pass_file.exists():
        raise FileNotFoundError(f'password file {pass_file} not found; run `solver user` to create the key')
    password: bytes = pass_file.read_bytes().strip()
    key = load_pem_private_key(key_file.read_bytes(), password=password or None)
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
def read_enc_key_file() -> dict[str, str]:
    """Read and parse keys/enc-key.json; raises FileNotFoundError if it has not been generated."""
    return cast(dict[str, str], loads(config['enc_key_file'].read_text()))


def verify_master_key(data: dict[str, str], master_key: bytes) -> bool:
    """Return True if `master_key` decrypts the stored `verify` ciphertext back to the known plaintext."""
    try:
        return decrypt_blob(bytes.fromhex(data['verify']), master_key) == bytes(config['verify_text'])
    except (InvalidTag, ValueError, KeyError):
        return False


@lru_cache(maxsize=None)
def read_master_key() -> bytes:
    """Unlock the current user's master key from keys/enc-key.json and prove it correct.

    Returns:
        The verified 32-byte master key.

    Raises:
        FileNotFoundError: If the private key, password, or enc-key file is missing.
        KeyError:          If the current user's public key has no entry in enc-key.json.
        ValueError:        If the key cannot be unwrapped or fails verification.
    Note: Used in solver.crypto.gitfilter; must not emit anything to stdout.
    """
    private_key: X25519PrivateKey = load_private_key()
    data: dict[str, str] = read_enc_key_file()
    my_public: str = public_key_hex(private_key.public_key())
    if my_public not in data:
        raise KeyError(f'public key {my_public} has no entry in {config["enc_key_file"]}')
    try:
        master_key: bytes = unlock(private_key, data[my_public])
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
