#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
The per-user vault: envelope encryption that makes a user's secrets opaque to the operator at rest.

Both the X25519 private key (`~/.euler/id`) and the project env (`~/.euler/env`) are stored
**encrypted** rather than plain. The scheme is standard envelope encryption (see
`docs/web-server-guide.md` § The vault):

- a random 32-byte **vault key** `VK` encrypts the secrets (AES-256-GCM, random nonce per blob);
- `VK` is stored **wrapped** under `PK = KDF(password, salt)` in `~/.euler/vault` -- so at
  rest the operator holds only `{salt, wrap(PK, VK)}` and the `VK`-ciphertext, and can decrypt
  none of it without the password. Changing the password **re-keys** the vault: a fresh `VK`, the
  few secret files re-encrypted under it, and the new `VK` wrapped under the new `PK` -- so a `VK`
  that leaked before the change opens nothing written after it (:func:`rekey_vault`).

`PK` is derived with **Argon2id** (:data:`~solver.crypto.wire.VAULT_KDF`: 64 MiB, 3 passes), over
the password and the vault's salt prefixed with `euler-vault-pk:` -- the browser derives the same
key from the password it already holds and the salt it gets in the SRP challenge, with the vendored
hash-wasm it also uses for the SRP key, whose label differs so the two never coincide. The vault
records its parameters, so the cost can rise later without stranding anybody.

**Key delivery.** The code that needs `VK` -- :func:`~solver.crypto.ciphers.load_private_key` and
the git clean/smudge filter -- runs as *subprocesses*, so `VK` cannot live only in the interactive
shell. It lives in a **uid-private tmpfs file** whose path is exported as `EULER_VAULT_KEY_FILE`
(:func:`session_vault_key` reads it); the key itself is never in any process's environment. The web
path writes that file from the `PK` the browser supplies at shell-attach.

**Where the terminal's password comes from**, in order: `$EULER_VAULT_PASSWORD` if set (a script,
CI, an automated run -- no prompt, no tty needed), otherwise the operator is **asked**, once, by the
shell (:func:`solver.crypto.keys.unlock_session`), which then materialises the key file for the
process tree. There is no password file: one stored next to the ciphertext it unlocks would hand the
password to exactly the reader the encryption is meant to stop, leaving the 0600 secrets dir as the
only real protection -- which is what the vault exists to improve on.

**The boundary, honestly:** this is at-rest opacity against a passive/honest operator only.
A malicious active root can read a live session's memory or alter the shared solver code -- no design
protects a secret from the entity that controls the CPU. Do not over-claim "zero-knowledge".

This module is imported on the git-filter path (via :mod:`solver.crypto.ciphers`), so its hard
contract is the same: **importing it, and everything it imports, emits nothing on stdout**, and it
depends only on the standard library, `cryptography`, :mod:`solver.config` and
:mod:`solver.crypto.wire`. All
interactive parts (password prompts, the `vault` command) live in :mod:`solver.crypto.keys`.
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
    'rekey_vault',
    'rekey_vault_with_pk',
    'replace_session_key',
    'reset_vault',
    'session_vault_key',
    'unlock_vault_with_pk',
    'unwrap_vault_key',
    'vault_exists',
    'wrap_vault_key',
    'write_session_key',
    'write_vault',
]

import os
from collections.abc import Callable
from functools import lru_cache
from json import dumps, loads
from pathlib import Path
from secrets import token_bytes
from tempfile import mkstemp
from typing import TypedDict, cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from solver.config import config
from solver.crypto import wire

_KEY_LEN: int = 32  # AES-256 / VK length
_SALT_LEN: int = 16  # matches the SRP salt width (euler_site.auth.srp)
_NONCE_LEN: int = 12  # AES-GCM nonce
_STAGED: str = '.rekey'  # suffix of a secret file re-encrypted under a new VK, not yet in place


class VaultData(TypedDict):
    """The on-disk `~/.euler/vault` body: the wrapped vault key and how its wrapping key is derived."""

    kdf: str  # the Argon2id parameters, `argon2id$m=…,t=…,p=…` (wire.VAULT_KDF when made)
    salt: str  # hex; the KDF salt (the SRP salt, so the browser derives the same PK)
    wrapped_vk: str  # hex (nonce | AES-GCM ciphertext of VK under PK)


# ==================================================================================================================== #
#                                       password key + vault-key wrap/unwrap
# ==================================================================================================================== #
def derive_password_key(password: str, salt: bytes, kdf: str | None = None) -> bytes:
    """Derive the 32-byte password key `PK`: Argon2id over the password and the labelled salt.

    *kdf* names the parameters (`argon2id$m=…,t=…,p=…`), defaulting to the current
    :data:`~solver.crypto.wire.VAULT_KDF`. The browser derives the identical key (`vault.js`), so
    the web path can supply `PK` without shipping the password to the server.

    Raises:
        ValueError: If *kdf* is not an Argon2id parameter string.
    """
    kdf = wire.VAULT_KDF if kdf is None else kdf
    secret: bytes = password.encode('utf-8')
    name, _, params = kdf.partition('$')
    try:
        values = dict(pair.split('=', 1) for pair in params.split(','))
        memory, passes, lanes = int(values['m']), int(values['t']), int(values['p'])
    except (KeyError, ValueError) as exc:
        raise ValueError(f'unsupported vault kdf: {kdf!r}') from exc
    if name != 'argon2id':
        raise ValueError(f'unsupported vault kdf: {kdf!r}')
    from argon2.low_level import Type, hash_secret_raw   # not on the git-filter path
    return hash_secret_raw(secret, wire.VAULT_ARGON2_LABEL + salt, passes, memory, lanes, _KEY_LEN, Type.ID)


def _vault_password_key(password: str, vault: VaultData) -> bytes:
    """`PK` for *vault*, derived the way that vault was made."""
    return derive_password_key(password, bytes.fromhex(vault['salt']), vault['kdf'])


def new_vault_key() -> bytes:
    """Return a fresh random 32-byte vault key (`VK`)."""
    return token_bytes(_KEY_LEN)


def wrap_vault_key(password_key: bytes, vault_key: bytes) -> str:
    """Wrap `vault_key` under `password_key` (AES-256-GCM, random nonce). Returns hex(nonce | ct)."""
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
    """Return True if `blob` carries the vault MAGIC header (i.e. is vault ciphertext, not plaintext)."""
    magic: bytes = wire.VAULT_MAGIC
    return blob[:len(magic)] == magic


def encrypt_secret(vault_key: bytes, plaintext: bytes) -> bytes:
    """Encrypt a secret under `VK` (AES-256-GCM, random nonce). Idempotent on already-encrypted input.

    Layout: `MAGIC | nonce(12) | ciphertext`. Unlike the git filter's convergent scheme this uses a
    random nonce -- these files are not tracked in git, so there is no reproducible-ciphertext need.
    """
    if is_vault_encrypted(plaintext):
        return plaintext
    magic: bytes = wire.VAULT_MAGIC
    nonce: bytes = token_bytes(_NONCE_LEN)
    return magic + nonce + AESGCM(vault_key).encrypt(nonce, plaintext, None)


def decrypt_secret(vault_key: bytes, blob: bytes) -> bytes:
    """Decrypt a blob produced by :func:`encrypt_secret`; pass-through for plaintext (no MAGIC).

    Raises:
        cryptography.exceptions.InvalidTag: If the blob is corrupt or the wrong key is used.
    """
    if not is_vault_encrypted(blob):
        return blob
    magic: int = len(wire.VAULT_MAGIC)
    nonce: bytes = blob[magic:magic + _NONCE_LEN]
    return AESGCM(vault_key).decrypt(nonce, blob[magic + _NONCE_LEN:], None)


# ==================================================================================================================== #
#                                               the vault file
# ==================================================================================================================== #
def vault_exists() -> bool:
    """Return True if this user's vault file is present (i.e. their secrets are vault-encrypted)."""
    return config.vault_file.exists()


def read_vault() -> VaultData | None:
    """Read and parse `~/.euler/vault`; return None if the user has no vault (plaintext at rest)."""
    vault_file: Path = config.vault_file
    if not vault_file.exists():
        return None
    return cast(VaultData, loads(vault_file.read_text()))


def write_vault(salt: bytes, wrapped_vk: str) -> None:
    """Serialise `~/.euler/vault` (0600) with the wrapped vault key, under the current KDF."""
    vault_file: Path = config.vault_file
    vault_file.parent.mkdir(parents=True, exist_ok=True)
    vault_file.parent.chmod(0o700)
    body: VaultData = {'kdf': wire.VAULT_KDF, 'salt': salt.hex(), 'wrapped_vk': wrapped_vk}
    _write_atomic(vault_file, dumps(body, indent=2).encode('utf-8'))


def _write_atomic(path: Path, data: bytes) -> None:
    """Write *path* (0600) through a sibling temp file and a rename: readers see old or new, never half."""
    fd, name = mkstemp(prefix=f'.{path.name}-', dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        os.write(fd, data)
    finally:
        os.close(fd)
    os.replace(name, path)


def _secret_files() -> list[Path]:
    """Every file the vault key may encrypt: `id`, its rolling backups, and `env`."""
    key_file: Path = config.private_key_file
    return [key_file, config.env_file] + [key_file.with_suffix(f'.{i}')
                                          for i in range(1, config.private_key_backups + 1)]


def init_vault(password: str, salt: bytes | None = None) -> bytes:
    """Create a fresh vault: mint `VK`, wrap it under `PK = KDF(password, salt)`, persist it.

    Returns the plaintext `VK` so the caller can immediately re-encrypt the existing secrets. When
    `salt` is omitted a random one is generated; the web path passes the account's SRP salt so the
    browser derives the same `PK`.
    """
    salt = token_bytes(_SALT_LEN) if salt is None else salt
    vault_key: bytes = new_vault_key()
    write_vault(salt, wrap_vault_key(derive_password_key(password, salt), vault_key))
    return vault_key


def unlock_vault(password: str) -> bytes:
    """Derive `PK` from `password` and the stored salt, then unwrap and return `VK`.

    Raises:
        FileNotFoundError:                  If no vault has been initialised.
        cryptography.exceptions.InvalidTag: If the password is wrong.
    """
    vault: VaultData | None = read_vault()
    if vault is None:
        raise FileNotFoundError(f'no vault at {config.vault_file}; run `vault --init`')
    vault_key: bytes = unwrap_vault_key(_vault_password_key(password, vault), vault['wrapped_vk'])
    _settle_rekey(vault_key)
    return vault_key


def encrypt_secret_files(vault_key: bytes) -> list[str]:
    """Encrypt any still-plaintext secret files (`id`, `env`) in place under `vault_key`.

    Idempotent (already-encrypted files are left alone). Returns the names of the files rewritten.
    Shared by the interactive `vault init` and the web first-login initialisation, so a vault is
    never created with its secrets left plain beside it.
    """
    encrypted: list[str] = []
    for path in (config.private_key_file, config.env_file):
        if not path.exists():
            continue
        raw: bytes = path.read_bytes()
        if is_vault_encrypted(raw):
            continue
        path.write_bytes(encrypt_secret(vault_key, raw))
        path.chmod(0o600)
        encrypted.append(path.name)
    return encrypted


def rekey_vault(old_password: str, new_password: str) -> bytes:
    """Change the vault password **and** its key: a fresh `VK`, wrapped under the new password.

    Every vault-encrypted secret file is re-encrypted under the new `VK` (:func:`_rekey`). Returns
    the new `VK`; the caller replaces the session key with it (:func:`replace_session_key`).

    Raises:
        cryptography.exceptions.InvalidTag: If `old_password` is wrong.
    """
    old_key: bytes = unlock_vault(old_password)
    salt: bytes = token_bytes(_SALT_LEN)
    return _rekey(old_key, salt, lambda new_key: wrap_vault_key(derive_password_key(new_password, salt), new_key))


def _rekey(old_key: bytes, salt: bytes, wrap: Callable[[bytes], str]) -> bytes:
    """Replace `VK`: re-encrypt the secret files under a fresh key, then commit the new wrapping.

    Crash-safe by one commit point. Each re-encrypted file is first **staged** beside its original
    (`<name>.rekey`); the vault file is then replaced atomically -- the commit -- and only after it
    are the staged files renamed over the originals. A crash before the commit leaves the old vault
    and files intact (the strays are dropped later); a crash after it leaves staged files that the
    new `VK` opens, and :func:`_settle_rekey` (run at every unlock) finishes the renames.
    """
    new_key: bytes = new_vault_key()
    staged: list[tuple[Path, Path]] = []
    for path in _secret_files():
        if not path.exists():
            continue
        blob: bytes = path.read_bytes()
        if not is_vault_encrypted(blob):
            continue
        target: Path = path.with_name(path.name + _STAGED)
        _write_atomic(target, encrypt_secret(new_key, decrypt_secret(old_key, blob)))
        staged.append((target, path))
    write_vault(salt, wrap(new_key))                      # the commit point
    for target, path in staged:
        os.replace(target, path)
    return new_key


def _settle_rekey(vault_key: bytes) -> None:
    """Finish or discard a re-key a crash interrupted: the vault's own `VK` decides.

    A staged file this `VK` opens belongs to the committed vault -- move it into place. One it does
    not open is from a re-key that never committed -- drop it. Cheap when there is nothing to do.
    """
    for path in _secret_files():
        target: Path = path.with_name(path.name + _STAGED)
        if not target.exists():
            continue
        try:
            decrypt_secret(vault_key, target.read_bytes())
        except InvalidTag:
            target.unlink(missing_ok=True)
        else:
            os.replace(target, path)


# ==================================================================================================================== #
#                                       web path: PK-based vault operations
# ==================================================================================================================== #
# The browser derives `PK` itself (Argon2id over the password it already holds and the SRP
# salt) and sends only `PK` to the user's own service -- the password
# never reaches any server, and the auth service never sees either. These are the `PK`-taking
# twins of the password functions above.

def unlock_vault_with_pk(password_key: bytes) -> bytes:
    """Unwrap and return `VK` using a browser-derived `PK` — derived the way this vault was made.

    Raises:
        FileNotFoundError:                  If no vault has been initialised.
        cryptography.exceptions.InvalidTag: If `PK` does not match the vault's wrapping (a stale
                                            vault after a password reset, or a wrong password).
    """
    vault: VaultData | None = read_vault()
    if vault is None:
        raise FileNotFoundError(f'no vault at {config.vault_file}')
    vault_key: bytes = unwrap_vault_key(password_key, vault['wrapped_vk'])
    _settle_rekey(vault_key)
    return vault_key


def init_vault_from_pk(password_key: bytes, salt: bytes) -> bytes:
    """Create a fresh vault wrapped under a browser-derived `PK` (web first-login).

    `salt` is the account's SRP salt, recorded so the terminal path (and any later browser session)
    derives the identical `PK`. Any plaintext `id`/`env` already on disk is encrypted in place --
    a vault must never coexist with plain secrets. Returns the plaintext `VK`.
    """
    vault_key: bytes = new_vault_key()
    write_vault(salt, wrap_vault_key(password_key, vault_key))
    encrypt_secret_files(vault_key)
    return vault_key


def rekey_vault_with_pk(old_password_key: bytes, new_password_key: bytes, new_salt: bytes) -> bytes:
    """Re-key the vault under a new browser-derived `PK` (a password change: the secrets survive).

    The `PK` twin of :func:`rekey_vault`: a fresh `VK`, the secret files re-encrypted under it, and
    the new `VK` wrapped under `new_password_key`. `new_salt` is the account's new SRP salt (the
    browser derived `new_password_key` from it, under the current KDF); `old_password_key` is derived
    with the vault's own recorded parameters. Returns the new `VK`.

    Raises:
        FileNotFoundError:                  If no vault has been initialised.
        cryptography.exceptions.InvalidTag: If `old_password_key` is wrong.
    """
    old_key: bytes = unlock_vault_with_pk(old_password_key)
    return _rekey(old_key, new_salt, lambda new_key: wrap_vault_key(new_password_key, new_key))


def reset_vault() -> list[str]:
    """Destroy the vault after a password reset: the secrets are unrecoverable *by design*.

    An SRP reset re-mints the login verifier but shares nothing with the vault, so the old `VK` can
    never be unwrapped again -- leaving the blobs around would only misrepresent the state. Removes the
    vault file and every **vault-encrypted** secret file (`id` + its rolling backups, `env`); plaintext
    files are never touched (they were never under this vault). Also drops the session key. Returns the
    names of the files removed; the user re-provisions (`user --regen` + re-upload) afterwards.
    """
    removed: list[str] = []
    vault_file: Path = config.vault_file
    if vault_file.exists():
        vault_file.unlink()
        removed.append(vault_file.name)
    for path in _secret_files():
        for candidate in (path, path.with_name(path.name + _STAGED)):
            if candidate.exists() and is_vault_encrypted(candidate.read_bytes()):
                candidate.unlink()
                removed.append(candidate.name)
    clear_session_key()
    return removed


# ==================================================================================================================== #
#                                               session vault key (VK delivery)
# ==================================================================================================================== #
def write_session_key(vault_key: bytes) -> Path:
    """Write `VK` to a fresh uid-private tmpfs file (0600) and export its path as the session key.

    Prefers `$XDG_RUNTIME_DIR` (a per-user tmpfs, cleared at logout); falls back to the system temp
    dir. Sets `EULER_VAULT_KEY_FILE` in this process's environment so child processes -- notably the
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
    os.environ[wire.VAULT_KEY_ENV] = name
    _resolve_session_key.cache_clear()
    return Path(name)


@lru_cache(maxsize=1)
def _resolve_session_key() -> bytes | None:
    """Resolve the session `VK` once per process: tmpfs key file first, else `$EULER_VAULT_PASSWORD`.

    Both sources are non-interactive by construction. This function is on the git-filter path, in a
    subprocess with no terminal and a stdout that belongs to git — it must never prompt. When neither
    source answers, the session is simply **locked**, and the interactive recovery is the shell's job
    (:func:`solver.crypto.keys.unlock_session`), which materialises the key file the fast path above
    then finds. There is deliberately no password *file*: a password at rest beside the ciphertext it
    unlocks protects nothing that the secrets dir's own 0600 does not already protect.
    """
    key_path: str = os.environ.get(wire.VAULT_KEY_ENV, '').strip()
    if key_path and (path := Path(key_path)).exists():
        data: bytes = path.read_bytes()
        if len(data) == _KEY_LEN:
            return data
    # The env password: a non-interactive unlock for a script or an automated run. Expensive (Argon2id)
    # per process, so a shell calls ensure_session_key() once at startup to materialise the tmpfs file
    # and let its children take the fast path above.
    password: str = os.environ.get(wire.VAULT_PASSWORD_ENV, '')
    if not (password and vault_exists()):
        return None
    try:
        return unlock_vault(password)
    except (InvalidTag, ValueError, OSError):
        return None


def session_vault_key() -> bytes | None:
    """Return the current session's vault key, or None if the vault is locked / not initialised.

    Read by :func:`~solver.crypto.ciphers.load_private_key`, the git filter, and
    :func:`~solver.ai.models.get_api_key` to decrypt vault secrets. Never emits to stdout.
    """
    return _resolve_session_key()


def replace_session_key(vault_key: bytes) -> Path:
    """Put a re-keyed `VK` into this session's key file **in place**, or write a fresh one.

    In place, at the same path, because other processes of this uid were handed that path (a
    web shell inherits it from its service), and a new file would strand them on a deleted one.
    They still hold the old `VK` in memory, which is why a re-key ends the session it ran in.
    """
    key_path: str = os.environ.get(wire.VAULT_KEY_ENV, '').strip()
    if not key_path or not Path(key_path).exists():
        return write_session_key(vault_key)
    _write_atomic(Path(key_path), vault_key)
    _resolve_session_key.cache_clear()
    return Path(key_path)


def clear_session_key() -> None:
    """Lock the session: delete the tmpfs key file, drop the env var, and clear the cached `VK`.

    Called on logout and vault reset so a torn-down session leaves no reachable key material.
    Idempotent.
    """
    key_path: str = os.environ.pop(wire.VAULT_KEY_ENV, '').strip()
    if key_path:
        Path(key_path).unlink(missing_ok=True)
    _resolve_session_key.cache_clear()


def ensure_session_key() -> bytes | None:
    """Establish the session key file for this process tree; return the `VK` (or None if locked).

    Idempotent: if `EULER_VAULT_KEY_FILE` already points at a valid key file, reuse it; otherwise
    derive `VK` from `$EULER_VAULT_PASSWORD` and materialise the tmpfs file so subprocesses (the
    git filter) skip the Argon2id cost. Non-interactive: a locked vault stays locked here and returns
    None -- asking the operator is :func:`solver.crypto.keys.unlock_session`, which is what a shell
    calls at startup.
    """
    key_path: str = os.environ.get(wire.VAULT_KEY_ENV, '').strip()
    if key_path and Path(key_path).exists():
        return session_vault_key()
    vault_key: bytes | None = session_vault_key()
    if vault_key is not None:
        write_session_key(vault_key)
    return vault_key
