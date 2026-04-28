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

from solver.config import keys_file, keys_version, schema_file, upload_keys_to_origin
from solver.crypto.asymmetrical import UserKeyPair
from solver.crypto.symmetrical import EncKey
from solver.utils import is_admin, is_unchanged, run_script

__all__ = ['get_key', 'get_master_key', 'get_user_key', 'read_keys_file', 'rekey_keys_file', 'write_keys_file']


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

    Clears the read and get_key caches after writing. If the file has changed relative
    to origin/master, the upload script is run (push for admin users, pull otherwise).

    Args:
        data: The full keys file contents to validate and persist.
    """
    _validate_schema(data)
    keys_file.write_text(dumps(data, indent=2))
    print(f'Keys file {keys_file} updated; num users: {len(data["users"])}, num keys: {len(data["keys"])}')
    get_key.cache_clear()
    read_keys_file.cache_clear()
    if not is_unchanged(keys_file):
        run_script(upload_keys_to_origin, cmd_line_args=['push' if is_admin() else 'pull'])


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
