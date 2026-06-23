#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Encrypted key file read/write and per-user key retrieval."""
from __future__ import annotations

__all__ = [
    'get_enc_key',
    'get_key',
    'get_master_key',
    'get_user_key',
    'read_keys_file',
    'rekey',
    'rekey_keys_file',
    'user',
    'write_keys_file',
]

from functools import lru_cache
from json import dumps, loads
from secrets import choice, token_bytes
from typing import Any

from jsonschema import validate

from solver.config import ExitCodes, config
from solver.crypto.asymmetrical import UserKeyPair
from solver.crypto.share import reconstruct_secret, split_secret
from solver.crypto.symmetrical import EncKey
from solver.shell import console, register
from solver.utils.gh import get_gh_user_email
from solver.utils.path_utils import write_file
from solver.utils.shell_utils import confirm


# ==================================================================================================================== #
#                                               keys-file read/write
# ==================================================================================================================== #

def _validate_schema(data: dict[str, Any]) -> None:
    """Validate data against the JSON schema, raising ValidationError on failure."""
    schema: dict[str, Any] = loads(config.schema_file.read_text())
    validate(instance=data, schema=schema)


@lru_cache(maxsize=None)
def read_keys_file() -> dict[str, Any]:
    """Read, schema-validate, and cache the keys-file, returning its parsed contents."""
    data: dict[str, Any] = loads(config.keys_file.read_text())
    _validate_schema(data)
    return data


def write_keys_file(data: dict[str, Any]) -> None:
    """
    Validate and write data to the keys-file, then sync it with the remote origin.

    Clears all key-related caches (keys file, master key, enc keys) after writing so that
    subsequent reads pick up the new content even after a master-key rotation.

    Args:
        data: The full keys file contents to validate and persist.
    """
    _validate_schema(data)
    config.keys_file.write_text(dumps(data, indent=2))
    console.print(f'[success]Keys file [accent]{config.keys_file}[/accent] updated; '
                  f'num users: {len(data["users"])}, num keys: {len(data["keys"])}[/success]')
    read_keys_file.cache_clear()
    get_master_key.cache_clear()
    _get_key_by_id.cache_clear()
    console.print('[muted]To sync with the remote origin, run [accent]`solver publish keys`[/accent][/muted]')


# ==================================================================================================================== #
#                                               get key / master key / user key
# ==================================================================================================================== #

@lru_cache(maxsize=None)
def _get_key_by_id(key_id: str) -> EncKey:
    """Return a decrypted EncKey for an explicit key id; cached per process."""
    master_key: bytes = get_master_key()
    data: dict[str, Any] = read_keys_file()
    return EncKey.from_dict(key_id, data['keys'][key_id], master_key=master_key)


def get_key(key_id: str | None = None) -> EncKey:
    """
    Return a decrypted EncKey, selecting a fresh random active key when no ID is given.

    Args:
        key_id: Hex UUID7 of the specific key to load. If None, a random active key is chosen
                on every call so encryption operations spread across the active key pool.

    Returns:
        The decrypted EncKey for the given or selected key ID.
    """
    if key_id is None:
        data: dict[str, Any] = read_keys_file()
        key_id, _ = choice([(k, v) for k, v in data['keys'].items() if v['status'] == 'active'])
    return _get_key_by_id(key_id)


@lru_cache(maxsize=None)
def get_master_key() -> bytes:
    """
    Decrypt and return the master key for the current user.

    Returns:
        The 32-byte master key, decrypted using the user's private key.

    Raises:
        ValueError: If the master key entry for this user is absent from keys.json.
    """
    user_key: UserKeyPair = get_user_key()
    enc_master_key: str | None = read_keys_file()['users'][user_key.user_email]['master_key']
    if enc_master_key is None:
        raise ValueError(f'Master key not found for user with email {user_key.user_email}')
    return user_key.unlock(enc_master_key)


@lru_cache(maxsize=None)
def get_user_key() -> UserKeyPair:
    """Load and cache the user key pair from the private key file on disk."""
    return UserKeyPair.from_file()


def get_enc_key(key_id: bytes | None = None) -> EncKey:
    """
    Look up an encryption key, returning a fresh active key when no ID is given.

    Args:
        key_id: Raw 16-byte key identifier. If None, a random active key is chosen per call.

    Returns:
        The EncKey matching the given ID, or a freshly chosen active key if key_id is None.
    """
    return get_key(None if key_id is None else key_id.hex())


# ==================================================================================================================== #
#                                               rekey keys file
# ==================================================================================================================== #
def rekey_keys_file(num_total_active_keys: int = 32, *, preserve_master: bool = True) -> int:
    """
    Reinitialize keys.json with additional new encryption keys.

    Generates enough new active keys to reach num_total_active_keys in total, optionally
    re-encrypting all key material under a new master key. Only accessible to admin users.
    Creates keys.json from scratch if it does not already exist.

    Args:
        num_total_active_keys: Target number of active keys in keys.json after rekeying. Defaults to 32.
        preserve_master:       If True, retain the existing master key; if False, generate a new one.
                               Defaults to True.
    """
    if get_gh_user_email() != config.author_email:
        console.print('[error]error:[/error] only the admin user may initialize the keys file')
        return ExitCodes.EXIT_ERROR
    user_key: UserKeyPair = get_user_key()
    new_master_key: bytes = token_bytes(32)
    if config.keys_file.exists():
        data: dict[str, Any] = read_keys_file()
        user_data = data['users'][user_key.user_email]
        master_key: bytes = user_key.unlock(user_data['master_key'])
        if preserve_master:
            new_master_key = master_key
        else:
            for key_id, raw_key in data['keys'].items():
                enc_key: EncKey = EncKey.from_dict(key_id, raw_key, master_key=master_key)
                raw_key['value'] = enc_key.as_dict(master_key=new_master_key)['value']
    else:
        data = {
            '$schema': config.schema_file.name,
            'version': config.keys_version,
            'users': {user_key.user_email: user_key.to_public_dict(new_master_key)},
            'keys': {}
        }
        preserve_master = False
    num_new_keys: int = num_total_active_keys - sum(1 for _, k in data['keys'].items() if k['status'] == 'active')
    if num_new_keys > 0:
        data['keys'].update({enc_key.id: enc_key.as_dict(master_key=new_master_key)
                             for enc_key in (EncKey.new('active') for _ in range(num_new_keys))})
    for email, raw_user in data['users'].items():
        if preserve_master is False or raw_user['master_key'] is None:
            raw_user['master_key'] = UserKeyPair.from_public_dict(email, raw_user).lock(new_master_key)
    write_keys_file(data)
    return ExitCodes.EXIT_OK


@register(help_text='Reinitialize keys.json with additional new encryption keys.')
def rekey(num_total_active_keys: int = 32, /, *, preserve_master: bool = True,
          backup: bool = False) -> int:
    """
    Reinitialize keys.json with additional new encryption keys.

    Generates enough new active keys to reach num_total_active_keys in total,
    optionally re-encrypting them under a new master key. Only accessible to admin users.

    Args:
        num_total_active_keys: Target number of active keys in keys.json after rekeying. Defaults to 32.
        preserve_master:       If True, retain the existing master key; if False, generate a new one.
                               Defaults to True.
        backup:                If True, print the backup keys for offline vault. Defaults to False.
    """
    if not confirm('Are you sure you want to rekey?'):
        console.print('[muted]Rekeying cancelled.[/muted]')
        return ExitCodes.EXIT_ERROR
    result = rekey_keys_file(num_total_active_keys, preserve_master=preserve_master)
    if backup:
        lines: dict[str, str] = {'private_key': config.private_key_file.read_text().strip(),
                                 **read_keys_file()['users'][get_user_key().user_email]}
        write_file(config.keys_backup_file, dumps(lines, indent=4).encode(), msg='keys backup')
    return result


# ==================================================================================================================== #
#                                               user
# ==================================================================================================================== #
@register(help_text='Show the current user\'s identity and master key access.')
def user(regen: bool = False) -> int:
    """
    Return the current user's identity alongside their master key access.

    Loads the X25519 private key from ~/.ssh/id_solver. If no private key exists there,
    or if regen is True, a new X25519 key pair is generated and the private key is persisted
    to ~/.ssh/id_solver. When a new key pair is generated, the corresponding public key entry
    is written to <repo>/keys/keys.json under the user's email:

        data['users'][user_key.user_email] = {
            "public_key": user_key.public_key.to_public_bytes().hex(),
            "master_key": user_key.lock(master_key) or None,
        }

    Run `solver upload_keys` to create a pull request with the updated keys/keys.json;
    the administrator will then add the encrypted master key for the new user.

    Note: generating a new key pair requires the GitHub CLI (gh) to be authenticated (gh auth login).

    Args:
        regen: If True, generate and persist a new key pair regardless of whether one already
               exists at ~/.ssh/id_solver. Defaults to False.

    Returns:
        A colour-coded string identifying the user and indicating whether they have
        access to the master key (✓ can encrypt/decrypt in green, ✗ cannot in red).
    """
    try:
        user_key: UserKeyPair | None = get_user_key()
    except (AssertionError, FileNotFoundError, ValueError):
        user_key = None
    try:
        master_key: bytes | None = get_master_key()
    except (AssertionError, FileNotFoundError, ValueError):
        master_key = None
    user_email: str = get_gh_user_email() if user_key is None else user_key.user_email
    if regen or user_key is None:
        new_user_key: UserKeyPair = UserKeyPair.new_persistent(user_email)
        get_user_key.cache_clear()
        data: dict[str, Any] = read_keys_file()
        data['users'][new_user_key.user_email] = new_user_key.to_public_dict(master_key)
        write_keys_file(data)
        user_key = new_user_key
    access_style = 'error' if master_key is None else 'success'
    access_mark = '✗ cannot' if master_key is None else '✓ can'
    console.print(f'[primary]{user_key!s}[/primary] [{access_style}]\n{access_mark} encrypt/decrypt[/{access_style}]')
    try:
        if user_key and master_key is None:
            register(help_text='Recover the master key from a list of shares.')(reconstruct)
        if user_key and user_key.user_email == config.author_email:
            register(help_text='Split the current master key into shares.')(split)
            register(help_text='Recover the master key from a list of shares.')(reconstruct)
    except ValueError:
        pass
    return ExitCodes.EXIT_OK if user_key is not None else ExitCodes.EXIT_ERROR


# ==================================================================================================================== #
#                                       n of m secret sharing for the master key
# ==================================================================================================================== #
def split(num_shares: int, threshold: int) -> int:
    try:
        master_key: bytes = get_master_key()
    except (AssertionError, FileNotFoundError, ValueError):
        console.print('[error]error:[/error] master key not found')
        return ExitCodes.EXIT_ERROR
    for i, share in enumerate(split_secret(master_key, num_shares=num_shares, threshold=threshold), start=1):
        console.print(f'[accent]Master key share {i} of {num_shares}:[/accent]\n[muted]{share}[/muted]\n\n')
    return ExitCodes.EXIT_OK


def reconstruct(threshold: int) -> int:
    """Recover the master key from a list of shares."""
    try:
        user_key: UserKeyPair = get_user_key()
    except (AssertionError, FileNotFoundError, ValueError):
        console.print('[error]error:[/error] user key not found, use `solver user` to generate one')
        return ExitCodes.EXIT_ERROR
    shares: list[str] = []
    for i in range(1, threshold + 1):
        share: str = console.input(f'[accent]Enter master key share {i} of {threshold}:[/accent] ').strip()
        shares.append(share)
        console.print(f'[primary]Share {i}/{threshold} recieved.[/primary]')
    try:
        master_key: bytes = reconstruct_secret(shares)
    except ValueError:
        console.print('[error]error:[/error] invalid shares')
        return ExitCodes.EXIT_ERROR
    console.print(f'[primary]Master key reconstructed from {threshold} shares:[/primary]')
    data: dict[str, Any] = read_keys_file()
    console.print('[muted]Updating keys.json with new master key...')
    data['users'][user_key.user_email] = user_key.to_public_dict(master_key)
    write_keys_file(data)
    get_master_key.cache_clear()
    console.print(f'[success]Master key successfully persisted from {threshold} shares.[/success]')
    return ExitCodes.EXIT_OK
