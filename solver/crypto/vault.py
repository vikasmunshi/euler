#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
The per-user vault: envelope encryption that makes a user's secrets opaque to the operator at rest.

Both the X25519 private key (`~/.euler/id`) and the project env (`~/.euler/env`) are stored
**encrypted** rather than plain. The scheme is standard envelope encryption (MT-6 of
`docs/real-multi-tenant-web-access.md`):

- a random 32-byte **vault key** ``VK`` encrypts the secrets (AES-256-GCM, random nonce per blob);
- ``VK`` is stored **wrapped** under ``PK = PBKDF2(password, salt)`` in ``~/.euler/vault`` -- so at
  rest the operator holds only ``{salt, wrap(PK, VK)}`` and the ``VK``-ciphertext, and can decrypt
  none of it without the password. Changing the password re-wraps only the tiny ``VK`` blob; the
  secrets are never re-encrypted.

``PK`` is derived with **PBKDF2-HMAC-SHA256** (not scrypt) on purpose: WebCrypto exposes PBKDF2
natively, so the browser can derive the identical ``PK`` from the password it already holds and the
salt it gets in the SRP challenge (MT-12), with no bundled KDF and no extra round-trip.

**Key delivery.** The code that needs ``VK`` -- :func:`~solver.crypto.ciphers.load_private_key` and
the git clean/smudge filter -- runs as *subprocesses*, so ``VK`` cannot live only in the interactive
shell. It lives in a **uid-private tmpfs file** whose path is exported as ``EULER_VAULT_KEY_FILE``
(:func:`session_vault_key` reads it); the key itself is never in any process's environment. The
terminal path bootstraps that file from ``~/.euler/user_pass`` (:func:`ensure_session_key`); the web
path writes it from the ``PK`` the browser supplies at shell-attach.

**The boundary, honestly (MT-6a):** this is at-rest opacity against a passive/honest operator only.
A malicious active root can read a live session's memory or alter the shared solver code -- no design
protects a secret from the entity that controls the CPU. Do not over-claim "zero-knowledge".

This module is imported on the git-filter path (via :mod:`solver.crypto.ciphers`), so its hard
contract is the same: **importing it, and everything it imports, emits nothing on stdout**, and it
depends only on the standard library, ``cryptography``, and :mod:`solver.crypto.config`. All
interactive parts (password prompts, the ``vault`` command) live in :mod:`solver.crypto.keys`.
"""
from __future__ import annotations

__all__ = [
    'clear_session_key',
    'decrypt_secret',
    'derive_password_key',
    'encrypt_secret',
    'encrypt_secret_files',
    'ensure_session_key',
    'init_vault',
    'init_vault_from_pk',
    'is_vault_encrypted',
    'new_vault_key',
    'read_vault',
    'reset_vault',
    'rewrap_vault',
    'rewrap_vault_with_pk',
    'session_vault_key',
    'unlock_vault_with_pk',
    'unwrap_vault_key',
    'vault_exists',
    'wrap_vault_key',
    'write_session_key',
    'write_vault',
]

import os
from functools import lru_cache
from json import dumps, loads
from pathlib import Path
from secrets import token_bytes
from tempfile import mkstemp
from typing import TypedDict, cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from solver.crypto.config import config

_KEY_LEN: int = 32  # AES-256 / VK length
_SALT_LEN: int = 16  # matches the SRP salt width (solver.web.auth.srp)
_NONCE_LEN: int = 12  # AES-GCM nonce


class VaultData(TypedDict):
    """The on-disk `~/.euler/vault` body: the wrapped vault key and how its wrapping key is derived."""

    kdf: str  # KDF identifier; only 'pbkdf2-sha256' is understood
    iterations: int  # PBKDF2 rounds used to derive PK from the password
    salt: str  # hex; PBKDF2 salt (the SRP salt, so the browser derives the same PK)
    wrapped_vk: str  # hex (nonce | AES-GCM ciphertext of VK under PK)


# ==================================================================================================================== #
#                                       password key + vault-key wrap/unwrap
# ==================================================================================================================== #
def derive_password_key(password: str, salt: bytes, iterations: int | None = None) -> bytes:
    """Derive the 32-byte password key ``PK`` from the password and salt (PBKDF2-HMAC-SHA256).

    WebCrypto-compatible: a browser derives the identical key from the same password, salt, and
    iteration count, so the web path can supply ``PK`` without shipping the password to the server.
    """
    rounds: int = config['vault_kdf_iterations'] if iterations is None else iterations
    return PBKDF2HMAC(SHA256(), _KEY_LEN, salt, rounds).derive(password.encode('utf-8'))


def new_vault_key() -> bytes:
    """Return a fresh random 32-byte vault key (``VK``)."""
    return token_bytes(_KEY_LEN)


def wrap_vault_key(password_key: bytes, vault_key: bytes) -> str:
    """Wrap ``vault_key`` under ``password_key`` (AES-256-GCM, random nonce). Returns hex(nonce | ct)."""
    nonce: bytes = token_bytes(_NONCE_LEN)
    return (nonce + AESGCM(password_key).encrypt(nonce, vault_key, None)).hex()


def unwrap_vault_key(password_key: bytes, wrapped: str) -> bytes:
    """Unwrap a vault key produced by :func:`wrap_vault_key`.

    Raises:
        cryptography.exceptions.InvalidTag: If the password key is wrong or the blob is corrupt.
    """
    raw: bytes = bytes.fromhex(wrapped)
    return AESGCM(password_key).decrypt(raw[:_NONCE_LEN], raw[_NONCE_LEN:], None)


# ==================================================================================================================== #
#                                       secret blob encrypt/decrypt (id, env)
# ==================================================================================================================== #
def is_vault_encrypted(blob: bytes) -> bool:
    """Return True if ``blob`` carries the vault MAGIC header (i.e. is vault ciphertext, not plaintext)."""
    magic: bytes = config['vault_magic']
    return blob[:len(magic)] == magic


def encrypt_secret(vault_key: bytes, plaintext: bytes) -> bytes:
    """Encrypt a secret under ``VK`` (AES-256-GCM, random nonce). Idempotent on already-encrypted input.

    Layout: ``MAGIC | nonce(12) | ciphertext``. Unlike the git filter's convergent scheme this uses a
    random nonce -- these files are not tracked in git, so there is no reproducible-ciphertext need.
    """
    if is_vault_encrypted(plaintext):
        return plaintext
    magic: bytes = config['vault_magic']
    nonce: bytes = token_bytes(_NONCE_LEN)
    return magic + nonce + AESGCM(vault_key).encrypt(nonce, plaintext, None)


def decrypt_secret(vault_key: bytes, blob: bytes) -> bytes:
    """Decrypt a blob produced by :func:`encrypt_secret`; pass-through for plaintext (no MAGIC).

    Raises:
        cryptography.exceptions.InvalidTag: If the blob is corrupt or the wrong key is used.
    """
    if not is_vault_encrypted(blob):
        return blob
    magic: int = len(config['vault_magic'])
    nonce: bytes = blob[magic:magic + _NONCE_LEN]
    return AESGCM(vault_key).decrypt(nonce, blob[magic + _NONCE_LEN:], None)


# ==================================================================================================================== #
#                                               the vault file
# ==================================================================================================================== #
def vault_exists() -> bool:
    """Return True if this user's vault file is present (i.e. their secrets are vault-encrypted)."""
    return config['vault_file'].exists()


def read_vault() -> VaultData | None:
    """Read and parse ``~/.euler/vault``; return None if the user has no vault (plaintext at rest)."""
    vault_file: Path = config['vault_file']
    if not vault_file.exists():
        return None
    return cast(VaultData, loads(vault_file.read_text()))


def write_vault(salt: bytes, wrapped_vk: str, iterations: int) -> None:
    """Serialise ``~/.euler/vault`` (0600) with the wrapped vault key and its KDF parameters."""
    vault_file: Path = config['vault_file']
    vault_file.parent.mkdir(parents=True, exist_ok=True)
    vault_file.parent.chmod(0o700)
    body: VaultData = {'kdf': 'pbkdf2-sha256', 'iterations': iterations,
                       'salt': salt.hex(), 'wrapped_vk': wrapped_vk}
    vault_file.write_text(dumps(body, indent=2))
    vault_file.chmod(0o600)


def init_vault(password: str, salt: bytes | None = None) -> bytes:
    """Create a fresh vault: mint ``VK``, wrap it under ``PK = PBKDF2(password, salt)``, persist it.

    Returns the plaintext ``VK`` so the caller can immediately re-encrypt the existing secrets. When
    ``salt`` is omitted a random one is generated; the web path passes the account's SRP salt so the
    browser derives the same ``PK``.
    """
    salt = token_bytes(_SALT_LEN) if salt is None else salt
    iterations: int = config['vault_kdf_iterations']
    vault_key: bytes = new_vault_key()
    password_key: bytes = derive_password_key(password, salt, iterations)
    write_vault(salt, wrap_vault_key(password_key, vault_key), iterations)
    return vault_key


def unlock_vault(password: str) -> bytes:
    """Derive ``PK`` from ``password`` and the stored salt, then unwrap and return ``VK``.

    Raises:
        FileNotFoundError:                  If no vault has been initialised.
        cryptography.exceptions.InvalidTag: If the password is wrong.
    """
    vault: VaultData | None = read_vault()
    if vault is None:
        raise FileNotFoundError(f'no vault at {config["vault_file"]}; run `vault --init`')
    password_key: bytes = derive_password_key(password, bytes.fromhex(vault['salt']), vault['iterations'])
    return unwrap_vault_key(password_key, vault['wrapped_vk'])


def encrypt_secret_files(vault_key: bytes) -> list[str]:
    """Encrypt any still-plaintext secret files (`id`, `env`) in place under ``vault_key``.

    Idempotent (already-encrypted files are left alone). Returns the names of the files rewritten.
    Shared by the interactive ``vault init`` and the web first-login initialisation, so a vault is
    never created with its secrets left plain beside it.
    """
    encrypted: list[str] = []
    for path in (config['private_key_file'], config['env_file']):
        if not path.exists():
            continue
        raw: bytes = path.read_bytes()
        if is_vault_encrypted(raw):
            continue
        path.write_bytes(encrypt_secret(vault_key, raw))
        path.chmod(0o600)
        encrypted.append(path.name)
    return encrypted


def rewrap_vault(old_password: str, new_password: str) -> None:
    """Change the vault password: unwrap ``VK`` with the old password, re-wrap under the new one.

    Only the small ``VK`` blob is rewritten; the ``VK``-encrypted secrets are untouched.

    Raises:
        cryptography.exceptions.InvalidTag: If ``old_password`` is wrong.
    """
    vault_key: bytes = unlock_vault(old_password)
    salt: bytes = token_bytes(_SALT_LEN)
    iterations: int = config['vault_kdf_iterations']
    write_vault(salt, wrap_vault_key(derive_password_key(new_password, salt, iterations), vault_key), iterations)


# ==================================================================================================================== #
#                                       web path: PK-based vault operations (MT-6/MT-12)
# ==================================================================================================================== #
# The browser derives ``PK`` itself (WebCrypto PBKDF2 over the password it already holds and the SRP
# salt) and sends only ``PK`` to the user's own service -- the password never reaches any server, and
# the auth service never sees either. These are the ``PK``-taking twins of the password functions above.

def unlock_vault_with_pk(password_key: bytes) -> bytes:
    """Unwrap and return ``VK`` using a browser-derived ``PK``.

    Raises:
        FileNotFoundError:                  If no vault has been initialised.
        cryptography.exceptions.InvalidTag: If ``PK`` does not match the vault's wrapping (a stale
                                            vault after a password reset, or a wrong password).
    """
    vault: VaultData | None = read_vault()
    if vault is None:
        raise FileNotFoundError(f'no vault at {config["vault_file"]}')
    return unwrap_vault_key(password_key, vault['wrapped_vk'])


def init_vault_from_pk(password_key: bytes, salt: bytes) -> bytes:
    """Create a fresh vault wrapped under a browser-derived ``PK`` (web first-login, MT-6).

    ``salt`` is the account's SRP salt, recorded so the terminal path (and any later browser session)
    derives the identical ``PK``. Any plaintext ``id``/``env`` already on disk is encrypted in place --
    a vault must never coexist with plain secrets. Returns the plaintext ``VK``.
    """
    iterations: int = config['vault_kdf_iterations']
    vault_key: bytes = new_vault_key()
    write_vault(salt, wrap_vault_key(password_key, vault_key), iterations)
    encrypt_secret_files(vault_key)
    return vault_key


def rewrap_vault_with_pk(old_password_key: bytes, new_password_key: bytes, new_salt: bytes) -> None:
    """Re-wrap ``VK`` under a new browser-derived ``PK`` (password change, MT-6c: the vault survives).

    Only the small ``VK`` blob is rewritten; the ``VK``-encrypted secrets are untouched. ``new_salt``
    is the account's new SRP salt (the browser derived ``new_password_key`` from it).

    Raises:
        FileNotFoundError:                  If no vault has been initialised.
        cryptography.exceptions.InvalidTag: If ``old_password_key`` is wrong.
    """
    vault_key: bytes = unlock_vault_with_pk(old_password_key)
    write_vault(new_salt, wrap_vault_key(new_password_key, vault_key), config['vault_kdf_iterations'])


def reset_vault() -> list[str]:
    """Destroy the vault after a password reset (MT-6c): the secrets are unrecoverable *by design*.

    An SRP reset re-mints the login verifier but shares nothing with the vault, so the old ``VK`` can
    never be unwrapped again -- leaving the blobs around would only misrepresent the state. Removes the
    vault file and every **vault-encrypted** secret file (`id` + its rolling backups, `env`); plaintext
    files are never touched (they were never under this vault). Also drops the session key. Returns the
    names of the files removed; the user re-provisions (``user --regen`` + re-upload) afterwards.
    """
    removed: list[str] = []
    vault_file: Path = config['vault_file']
    if vault_file.exists():
        vault_file.unlink()
        removed.append(vault_file.name)
    key_file: Path = config['private_key_file']
    candidates: list[Path] = [key_file, config['env_file']]
    candidates += [key_file.with_suffix(f'.{i}') for i in range(1, config['private_key_backups'] + 1)]
    for path in candidates:
        if path.exists() and is_vault_encrypted(path.read_bytes()):
            path.unlink()
            removed.append(path.name)
    clear_session_key()
    return removed


# ==================================================================================================================== #
#                                               session vault key (VK delivery)
# ==================================================================================================================== #
def write_session_key(vault_key: bytes) -> Path:
    """Write ``VK`` to a fresh uid-private tmpfs file (0600) and export its path as the session key.

    Prefers ``$XDG_RUNTIME_DIR`` (a per-user tmpfs, cleared at logout); falls back to the system temp
    dir. Sets ``EULER_VAULT_KEY_FILE`` in this process's environment so child processes -- notably the
    git clean/smudge filter -- inherit it. Returns the file path.
    """
    runtime: str = os.environ.get('XDG_RUNTIME_DIR', '').strip()
    directory: str | None = None
    if runtime:
        euler_run: Path = Path(runtime) / 'euler'
        euler_run.mkdir(parents=True, exist_ok=True)
        euler_run.chmod(0o700)
        directory = str(euler_run)
    fd, name = mkstemp(prefix='vk-', dir=directory)  # dir=None → the system temp dir (also uid-private)
    try:
        os.fchmod(fd, 0o600)
        os.write(fd, vault_key)
    finally:
        os.close(fd)
    os.environ[config['vault_key_env']] = name
    _resolve_session_key.cache_clear()
    return Path(name)


@lru_cache(maxsize=1)
def _resolve_session_key() -> bytes | None:
    """Resolve the session ``VK`` once per process: tmpfs key file first, else the terminal password."""
    key_path: str = os.environ.get(config['vault_key_env'], '').strip()
    if key_path and (path := Path(key_path)).exists():
        data: bytes = path.read_bytes()
        if len(data) == _KEY_LEN:
            return data
    # Terminal bootstrap: derive VK from the at-rest password. Expensive (PBKDF2), so a shell should
    # call ensure_session_key() at startup to materialise the tmpfs file and take the fast path above.
    pass_file: Path = config['user_pass_file']
    if not (pass_file.exists() and vault_exists()):
        return None
    try:
        return unlock_vault(pass_file.read_text().rstrip('\n'))
    except (InvalidTag, ValueError, OSError):
        return None


def session_vault_key() -> bytes | None:
    """Return the current session's vault key, or None if the vault is locked / not initialised.

    Read by :func:`~solver.crypto.ciphers.load_private_key`, the git filter, and
    :func:`~solver.ai.models.get_api_key` to decrypt vault secrets. Never emits to stdout.
    """
    return _resolve_session_key()


def clear_session_key() -> None:
    """Lock the session: delete the tmpfs key file, drop the env var, and clear the cached ``VK``.

    Called on logout (DD-14) and vault reset so a torn-down session leaves no reachable key material.
    Idempotent.
    """
    key_path: str = os.environ.pop(config['vault_key_env'], '').strip()
    if key_path:
        Path(key_path).unlink(missing_ok=True)
    _resolve_session_key.cache_clear()


def ensure_session_key() -> bytes | None:
    """Establish the session key file for this process tree; return the ``VK`` (or None if locked).

    Idempotent: if ``EULER_VAULT_KEY_FILE`` already points at a valid key file, reuse it; otherwise, on
    the terminal path, derive ``VK`` from ``~/.euler/user_pass`` and materialise the tmpfs file so
    subprocesses (the git filter) skip the PBKDF2 cost. A shell calls this once at startup.
    """
    key_path: str = os.environ.get(config['vault_key_env'], '').strip()
    if key_path and Path(key_path).exists():
        return session_vault_key()
    vault_key: bytes | None = session_vault_key()
    if vault_key is not None:
        write_session_key(vault_key)
    return vault_key
