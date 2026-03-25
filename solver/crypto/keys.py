#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from _sha2 import sha256
from functools import lru_cache
from json import dumps, loads
from os import environ
from pathlib import Path
from secrets import token_bytes
from subprocess import CalledProcessError, run as subprocess_run
from typing import Literal, NamedTuple
from uuid import UUID, uuid7

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from solver.crypto.user import UserIdentity, get_user, lock, unlock

__all__ = ['SymmetricalKey', 'get_key', 'get_default_key']

_keys_file: Path = Path(__file__).parent / 'keys.json'
_keys_version: str = '1.0.1'
_master_user: str = 'vikas.munshi@gmail.com'
_schema_file: Path = Path(__file__).parent / 'keys.schema.json'
_repo_root: Path = Path(__file__).parent.parent.parent


class SymmetricalKey(NamedTuple):
    """Named tuple representing an encryption key with id, value, and status.

    Attributes:
        id: UUID7 hex string
        value: 32-byte AES-256 key
        status: default or active or retired
    """
    id: str
    value: bytes
    status: Literal['default', 'active', 'retired', 'unmanaged']

    def __repr__(self) -> str:
        return f'Key(id=...{self.id[-8:]}, value={self.value.hex()[:8]}..., status={self.status})'

    @classmethod
    def new(cls) -> SymmetricalKey:
        value: bytes = bytes.fromhex(sha256(b''.join(token_bytes(32) for _ in range(32 // 4))).hexdigest())
        return cls(id=uuid7().hex, value=value, status='active')

    @classmethod
    def from_dict(cls, data: dict[str, ...], master_key: bytes) -> SymmetricalKey:
        assert UUID(hex=data['id']).version == 7, f"key id '{data['id']}' must be UUID version 7"
        value_bytes: bytes = bytes.fromhex(data['value'])
        nonce: bytes = value_bytes[:12]
        ciphertext: bytes = value_bytes[12:]
        key_bytes: bytes = AESGCM(master_key).decrypt(nonce, ciphertext, None)
        assert len(key_bytes) == 32, f"key '{data['id']}' must be 32 bytes long"
        return cls(id=data['id'], value=key_bytes, status=data['status'])

    def as_dict(self, master_key: bytes) -> dict[str, ...]:
        nonce: bytes = token_bytes(12)
        ciphertext: bytes = AESGCM(master_key).encrypt(nonce, self.value, None)
        return {'id': self.id, 'value': (nonce + ciphertext).hex(), 'status': self.status}


def _add_keys(num_new_keys: int) -> None:
    user_identity: UserIdentity = get_user()
    if user_identity.email != _master_user:
        return
    if _keys_file.exists():
        data: dict[str, ...] = loads(_keys_file.read_text())
        _validate_data(data)
        enc_master_key: str = next(user['master_key'] for user in data['users'] if user['email'] == user_identity.email)
        master_key: bytes = unlock(enc_master_key)
    else:
        master_key = SymmetricalKey.new().value
        enc_master_key = lock(master_key)
        data = {
            '$schema': './keys.schema.json',
            'version': _keys_version,
            'default': None,
            'keys': [],
            'users': [
                {'email': user_identity.email,
                 'public_key': user_identity.public_key_str,
                 'master_key': enc_master_key, },
            ],
        }
        num_new_keys = num_new_keys if num_new_keys > 0 else 16
    data['keys'].extend(SymmetricalKey.new().as_dict(master_key) for _ in range(num_new_keys))
    if data['default'] is None:
        data['default'] = next(key['id'] for key in data['keys'] if key['status'] == 'active')
    new_users: bool = False
    for user in data['users']:
        if user.get('master_key') is None:
            user_key = UserIdentity.from_dict({'email': user['email'], 'public_key': user['public_key']})
            user['master_key'] = lock(master_key, user_key=user_key)
            new_users = True
    if num_new_keys > 0 or new_users:
        write_keys_file(data)


def _validate_data(data: dict[str, ...]) -> None:
    schema: dict[str, ...] = loads(_schema_file.read_text())
    validate(instance=data, schema=schema)
    key_ids: set[str] = {key['id'] for key in data['keys']}
    if data['default'] not in key_ids:
        raise ValueError(f"default key '{data['default']}' not found in keys")
    default_key = next(k for k in data['keys'] if k['id'] == data['default'])
    if default_key['status'] != 'active':
        raise ValidationError(f"default key must have status 'active', got '{default_key['status']}'")


@lru_cache(maxsize=None)
def read_keys_file() -> dict[str, ...]:
    if get_user().email == _master_user:
        _add_keys(0)
    data: dict[str, ...] = loads(_keys_file.read_text())
    _validate_data(data)
    return data


def write_keys_file(data: dict[str, ...], *, keys_file: Path) -> None:
    _validate_data(data)
    keys_file.write_text(dumps(data, indent=2))
    for func in (read_keys_file, get_key, get_default_key):
        func.cache_clear()


def _add_user(user: UserIdentity) -> None:
    print(f"User with email '{user.email}' not found in keys file, adding user to keys file")
    data: dict[str, ...] = read_keys_file()
    data['users'].append({'email': user.email, 'public_key': user.public_key_str, 'master_key': None})
    write_keys_file(data)
    print(f'You have been added to the keys file at {_keys_file.name}')
    print(f'To continue, we will commit, push, and create a PR')
    user_response: str = input(f"Continue [Y/n]: ")
    if user_response.lower() != 'y':
        print(f'Please push the file {_keys_file.as_posix()} to the remote repository, and create a PR.')
        return
    branch_name: str = f'add-keys-{user.email.replace("@", "-at-").replace(".", "-")}'
    script_path: Path = Path(__file__).parent / 'push_keys_file.sh'
    env = {**environ, 'USER_ID': user.email, 'BRANCH_NAME': branch_name, 'FILE_TO_PUSH': _keys_file.as_posix()}
    try:
        subprocess_run([script_path.as_posix()], cwd=_repo_root, env=env, check=True, text=True)
        print(f'Successfully pushed known keys for {user.email} to branch {branch_name}')
    except CalledProcessError as e:
        print(f'Failed to push keys: {e}')


def _get_master_key(users: list[dict[str, ...]]) -> bytes:
    user: UserIdentity = get_user()
    try:
        user_data = next(raw_user for raw_user in users if raw_user['email'] == user.email)
    except StopIteration:
        _add_user(user)
        raise ValueError(f"User with email '{user.email}' not found in keys file")
    enc_master_key: str = user_data.get('master_key')
    if enc_master_key is None:
        raise ValueError(f"Master key not found for user with email '{user.email}'")
    master_key: bytes = unlock(enc_master_key)
    return master_key


@lru_cache(maxsize=None)
def get_key(key_id: str) -> SymmetricalKey:
    data: dict[str, ...] = read_keys_file()
    master_key: bytes = _get_master_key(data['users'])
    try:
        return next(SymmetricalKey.from_dict(raw_key, master_key)
                    for raw_key in data['keys'] if raw_key['id'] == key_id)
    except StopIteration:
        raise KeyError(f"Key with ID '{key_id}' not found")


@lru_cache(maxsize=None)
def get_default_key() -> SymmetricalKey:
    data: dict[str, ...] = read_keys_file()
    default_id: str = data['default']
    master_key: bytes = _get_master_key(data['users'])
    return next(SymmetricalKey.from_dict(raw_key, master_key)
                for raw_key in data['keys'] if raw_key['id'] == default_id)
