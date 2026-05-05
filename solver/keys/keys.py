#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Encrypted key file read/write and per-user key retrieval."""
from __future__ import annotations

from functools import lru_cache
from json import dumps
from json import loads
from secrets import choice, token_bytes
from typing import Any

from jsonschema import validate

from solver.config import ColorCodes, keys_backup_file, keys_file, keys_version, private_key_file, schema_file
from solver.keys.asymmetrical import UserKeyPair
from solver.keys.symmetrical import EncKey
from solver.utils.utils import is_admin, write_file


# ==================================================================================================================== #
#                                               keys-file read/write
# ==================================================================================================================== #

def _validate_schema(data: dict[str, Any]) -> None:
    """Validate data against the keys file JSON schema, raising jsonschema.ValidationError on failure."""
    schema: dict[str, Any] = loads(schema_file.read_text())
    validate(instance=data, schema=schema)


@lru_cache(maxsize=None)
def read_keys_file() -> dict[str, Any]:
    """Read, schema-validate, and cache the keys file, returning its parsed contents."""
    data: dict[str, Any] = loads(keys_file.read_text())
    _validate_schema(data)
    return data


def write_keys_file(data: dict[str, Any]) -> None:
    """
    Validate and write data to the keys file, then sync it with the remote origin.

    Clears the read and get_key caches after writing.

    Args:
        data: The full keys file contents to validate and persist.
    """
    _validate_schema(data)
    keys_file.write_text(dumps(data, indent=2))
    print(f'Keys file {keys_file} updated; num users: {len(data["users"])}, num keys: {len(data["keys"])}')
    get_key.cache_clear()
    read_keys_file.cache_clear()


# ==================================================================================================================== #
#                                               get key / master key / user key
# ==================================================================================================================== #

@lru_cache(maxsize=None)
def get_key(key_id: str | None = None) -> EncKey:
    """
    Return a decrypted EncKey, selecting a random active key when no ID is given.

    Args:
        key_id: Hex UUID7 of the specific key to load. If None, a random active key is chosen.

    Returns:
        The decrypted EncKey for the given or selected key ID.
    """
    master_key: bytes = get_master_key()
    data: dict[str, Any] = read_keys_file()
    if key_id is None:
        selected_id, selected = choice([(k, v) for k, v in data['keys'].items() if v['status'] == 'active'])
    else:
        selected_id, selected = key_id, data['keys'][key_id]
    return EncKey.from_dict(selected_id, selected, master_key=master_key)


@lru_cache(maxsize=None)
def get_master_key() -> bytes:
    """
    Decrypt and return the master key for the current user.

    Returns:
        The 32-byte master key, decrypted using the user's private key.

    Raises:
        AssertionError: If the master key entry for this user is absent from keys.json.
    """
    user_key: UserKeyPair = get_user_key()
    enc_master_key: str | None = read_keys_file()['users'][user_key.user_email]['master_key']
    assert enc_master_key is not None, f"Master key not found for user with email '{user_key.user_email}'"
    return user_key.unlock(enc_master_key)


@lru_cache(maxsize=None)
def get_user_key() -> UserKeyPair:
    """Load and cache the user key pair from the private key file on disk."""
    return UserKeyPair.from_file()


# ==================================================================================================================== #
#                                               user
# ==================================================================================================================== #
def user(regen: bool = False) -> str:
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
    except (AssertionError, FileNotFoundError):
        user_key = None
    try:
        master_key: bytes | None = get_master_key()
    except (AssertionError, FileNotFoundError):
        master_key = None
    if regen or user_key is None:
        user_key = UserKeyPair.new_persistent()
        get_user_key.cache_clear()
        data: dict[str, Any] = read_keys_file()
        data['users'][user_key.user_email] = user_key.to_public_dict(master_key)
        write_keys_file(data)
    return (f'{user_key!s} '
            f'{(ColorCodes.RED + "(✗ cannot") if master_key is None else (ColorCodes.GREEN + "(✓ can")} '
            f'encrypt/decrypt){ColorCodes.RESET}')


# ==================================================================================================================== #
#                                               rekey keys file
# ==================================================================================================================== #

def rekey_keys_file(num_total_active_keys: int = 32, *, preserve_master: bool = True) -> None:
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
    if not is_admin():
        print('only admin user should initialize keys file')
        return
    user_key: UserKeyPair = get_user_key()
    new_master_key: bytes = token_bytes(32)
    if keys_file.exists():
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
            '$schema': schema_file.name,
            'version': keys_version,
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


def rekey(num_total_active_keys: int = 32, /, *, preserve_master: bool = True, backup: bool = False) -> None:
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
    confirmation = input("Are you sure you want to rekey? Type 'Yes' to confirm: ")
    if confirmation != "Yes":
        print("Rekeying cancelled.")
        return

    rekey_keys_file(num_total_active_keys, preserve_master=preserve_master)
    if backup:
        lines: dict[str, str] = {
            'private_key': private_key_file.read_text().strip(),
            **read_keys_file()['users'][get_user_key().user_email]
        }
        write_file(keys_backup_file, dumps(lines, indent=4).encode(), msg='keys backup')


__all__ = (
    'get_key',
    'get_master_key',
    'get_user_key',
    'rekey',
    'rekey_keys_file',
    'user',
    'write_keys_file',
)
