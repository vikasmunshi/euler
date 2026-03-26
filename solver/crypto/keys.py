#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from _sha2 import sha256
from functools import lru_cache
from json import dumps, loads
from secrets import choice, token_bytes
from typing import Any, Literal, NamedTuple, cast
from uuid import UUID, uuid7

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jsonschema import validate

from solver.crypto.error import error_handler
from solver.crypto.user import UserIdentity, get_user, unlock
from solver.workspace import keys_file, schema_file

__all__ = ['SymmetricalKey', 'get_key', 'get_key', 'read_keys_file', 'write_keys_file']

Status = Literal['active', 'reserved', 'retired', 'unmanaged']


class SymmetricalKey(NamedTuple):
    """Named tuple representing an encryption key with id, value, and status.

    Attributes:
        id: UUID7 hex string
        value: 32-byte AES-256 key
        status: default or active or retired
    """
    id: str
    value: bytes
    status: Status

    def __repr__(self) -> str:
        return f'Key(id=...{self.id[-8:]}, value={self.value.hex()[:8]}..., status={self.status})'

    @classmethod
    def new(cls, status: Status = 'unmanaged') -> SymmetricalKey:
        value: bytes = bytes.fromhex(sha256(b''.join(token_bytes(32) for _ in range(32 // 4))).hexdigest())
        return cls(id=uuid7().hex, value=value, status=status)

    @classmethod
    def from_dict(cls, data: dict[str, str], master_key: bytes) -> SymmetricalKey:
        assert UUID(hex=data['id']).version == 7, f"key id '{data['id']}' must be UUID version 7"
        value_bytes: bytes = bytes.fromhex(data['value'])
        nonce: bytes = value_bytes[:12]
        ciphertext: bytes = value_bytes[12:]
        key_bytes: bytes = AESGCM(master_key).decrypt(nonce, ciphertext, None)
        assert len(key_bytes) == 32, f"key '{data['id']}' must be 32 bytes long"
        return cls(id=data['id'], value=key_bytes, status=cast(Status, data['status']))

    def as_dict(self, master_key: bytes) -> dict[str, str]:
        nonce: bytes = token_bytes(12)
        ciphertext: bytes = AESGCM(master_key).encrypt(nonce, self.value, None)
        return {'id': self.id, 'value': (nonce + ciphertext).hex(), 'status': self.status}


def _validate_data(data: dict[str, Any]) -> None:
    schema: dict[str, Any] = loads(schema_file.read_text())
    validate(instance=data, schema=schema)


@lru_cache(maxsize=None)
def read_keys_file() -> dict[str, Any]:
    data: dict[str, Any] = loads(keys_file.read_text())
    _validate_data(data)
    return data


def write_keys_file(data: dict[str, Any]) -> None:
    _validate_data(data)
    keys_file.write_text(dumps(data, indent=2))
    for func in (read_keys_file, get_key):
        func.cache_clear()


@lru_cache(maxsize=None)
@error_handler('get key')
def get_key(key_id: str | None = None) -> SymmetricalKey:
    user: UserIdentity = get_user()
    data: dict[str, Any] = read_keys_file()
    user_data = next(raw_user for raw_user in data['users'] if raw_user['email'] == user.email)
    enc_master_key: str = user_data['master_key']
    assert enc_master_key is not None, f"Master key not found for user with email '{user.email}'"
    master_key: bytes = unlock(enc_master_key)
    if key_id is None:
        selected: dict[str, str] = choice([raw for raw in data['keys'] if raw['status'] == 'active'])
    else:
        selected = next(raw for raw in data['keys'] if raw['id'] == key_id)
    return SymmetricalKey.from_dict(selected, master_key)
