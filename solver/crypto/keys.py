#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from _sha2 import sha256
from collections import namedtuple
from functools import lru_cache
from json import dumps, loads
from pathlib import Path
from secrets import token_bytes
from typing import Literal
from uuid import UUID, uuid7

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from solver.workspace import BASE_DIR

__all__ = ['_keys_file', '_keys_version', '_master_flag',
           'Key', 'load_keys', 'read_keys_file', 'get_key', 'get_default_key', ]

_keys_file: Path = BASE_DIR / 'keys' / 'keys.json'
_keys_version: str = '1.0.1'
_master_flag: Path = (_keys_file.parent / 'master')
_schema_file: Path = Path(__file__).parent / 'keys.schema.json'
_key_size: int = 32  # AES-256 requires 32 bytes (256 bits)
_key_str_size: int = 16
Key = namedtuple('Key', ['id', 'value', 'status'])
Key.__doc__ = ('Named tuple representing an encryption key with id, value, and status.\n'
               'attributes:\n'
               '  id: UUID7 hex string\n'
               '  value: 32-byte AES-256 key\n'
               '  status: default or active or retired\n')
Key.__repr__ = lambda self: f'Key(id=...{self.id[-8:]}, value={self.value.hex()[:8]}..., status={self.status})'


def _add_keys(num_new_keys: int, *, keys_file: Path) -> None:
    if keys_file.exists():
        data: dict[str, ...] = read_keys_file(keys_file=keys_file)
    else:
        data: dict[str, ...] = {
            '$schema': './keys.schema.json',
            'description': 'AES-256 encryption keys for solver',
            'version': _keys_version,
            'default': None,
            'keys': [],
        }
    data['keys'].extend(
        {'id': uuid7().hex,
         'value': sha256(b''.join(token_bytes(_key_size) for _ in range(_key_size // 4))).hexdigest(),
         'status': 'active', }
        for _ in range(num_new_keys))
    if data['default'] is None:
        data['default'] = next(key['id'] for key in data['keys'] if key['status'] == 'active')
    (keys_file.parent / _schema_file.name).write_text(_schema_file.read_text())
    write_keys_file(data, keys_file=keys_file)


def _set_default_key(key_id: str, *, keys_file: Path) -> None:
    data: dict[str, ...] = read_keys_file(keys_file=keys_file)
    key_ids: set[str] = set(k['id'] for k in data['keys'])
    if key_id not in key_ids:
        raise ValueError(f"Key ID {key_id} not found in keys")
    data['default'] = key_id
    write_keys_file(data, keys_file=keys_file)


def _retire_keys(key_ids: list[str], *, keys_file: Path) -> None:
    data: dict[str, ...] = read_keys_file(keys_file=keys_file)
    for key in data['keys']:
        if key['id'] in set(key_ids) and key['id'] != data['default']:
            key['status'] = 'retired'
    write_keys_file(data, keys_file=keys_file)


def _delete_keys(key_ids: list[str], *, keys_file: Path) -> None:
    data: dict[str, ...] = read_keys_file(keys_file=keys_file)
    data['keys'] = [key for key in data['keys'] if key['id'] not in set(key_ids) or key['status'] == 'active']
    write_keys_file(data, keys_file=keys_file)


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
def read_keys_file(*, keys_file: Path) -> dict[str, ...]:
    data: dict[str, ...] = loads(keys_file.read_text())
    _validate_data(data)
    return data


def write_keys_file(data: dict[str, ...], *, keys_file: Path) -> None:
    _validate_data(data)
    keys_file.write_text(dumps(data, indent=2))
    for func in (load_keys, read_keys_file, get_key, get_default_key):
        func.cache_clear()


@lru_cache(maxsize=None)
def load_keys(*, keys_file: Path) -> list[Key]:
    if not keys_file.exists():
        if _master_flag.exists():
            _add_keys(num_new_keys=16, keys_file=keys_file)
        else:
            raise RuntimeError('Encryption keys not available, run key_exchange first')
    data: dict[str, ...] = read_keys_file(keys_file=keys_file)
    default_key_id: UUID = UUID(hex=data['default'])
    keys: list[tuple[str, bytes, Literal['active', 'retired', 'default']]] = []
    for raw_key in data['keys']:
        key_uuid: UUID = UUID(hex=raw_key['id'])
        assert key_uuid.version == 7, f"key id '{key_uuid}' must be version 7"
        key_bytes: bytes = bytes.fromhex(raw_key['value'])
        assert len(key_bytes) == _key_size, f"key '{key_uuid}' must be {_key_size} bytes long"
        keys.append(Key(key_uuid.hex, key_bytes, 'default' if key_uuid == default_key_id else raw_key['status']))
    return sorted(keys, key=lambda k: k[0])


@lru_cache(maxsize=None)
def get_key(key_id: str, /, *, keys_file: Path = _keys_file) -> Key:
    keys = load_keys(keys_file=keys_file)
    try:
        return next(key for key in keys if key[0] == key_id)
    except StopIteration:
        raise KeyError(f"Key with ID '{key_id}' not found")


@lru_cache(maxsize=None)
def get_default_key(*, keys_file: Path = _keys_file) -> Key:
    keys = load_keys(keys_file=keys_file)
    try:
        return next(key for key in keys if key[2] == 'default')
    except StopIteration:
        raise ValueError("No default key found")
