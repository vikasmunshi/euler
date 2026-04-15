#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import lru_cache
from json import dumps
from json import loads
from pathlib import Path
from re import match
from secrets import choice, token_bytes
from subprocess import CalledProcessError, run as subprocess_run
from typing import Any, Literal, cast
from typing import NamedTuple
from uuid import UUID, uuid7

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from jsonschema import validate

from solver.crypto.error import error_handler

__all__ = ['SymmetricalKey', 'AsymmetricalKey', 'get_key', 'get_user_key', 'get_user_email', 'lock', 'unlock', ]

admin_user: str = 'vikas.munshi@gmail.com'
keys_file: Path = Path(__file__).parent / 'keys.json'
keys_version: str = '1.0.1'
private_key_file: Path = Path.home() / '.ssh' / 'id_solver'
schema_file: Path = Path(__file__).parent / 'schema.json'


class SymmetricalKey(NamedTuple):
    """Named tuple representing an encryption key with id, value, and status.

    Attributes:
        id: UUID7 hex string
        value: 32-byte AES-256 key
        status: active, reserved, retired, or unmanaged
    """
    id: str
    value: bytes
    status: Literal['active', 'reserved', 'retired', 'unmanaged']

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id=...{self.id[-8:]}, value={self.value.hex()[:8]}..., status={self.status})'

    @classmethod
    def new(cls, status: Literal['active', 'reserved', 'retired', 'unmanaged'] = 'unmanaged') -> SymmetricalKey:
        value: bytes = token_bytes(32)
        return cls(id=uuid7().hex, value=value, status=status)

    @classmethod
    def from_dict(cls, data: dict[str, str], master_key: bytes) -> SymmetricalKey:
        assert UUID(hex=data['id']).version == 7, f"key id '{data['id']}' must be UUID version 7"
        value_bytes: bytes = bytes.fromhex(data['value'])
        nonce: bytes = value_bytes[:12]
        ciphertext: bytes = value_bytes[12:]
        key_bytes: bytes = AESGCM(master_key).decrypt(nonce, ciphertext, None)
        assert len(key_bytes) == 32, f"key '{data['id']}' must be 32 bytes long"
        status = cast(Literal['active', 'reserved', 'retired', 'unmanaged'], data['status'])
        return cls(id=data['id'], value=key_bytes, status=status)

    def as_dict(self, master_key: bytes) -> dict[str, str]:
        nonce: bytes = token_bytes(12)
        ciphertext: bytes = AESGCM(master_key).encrypt(nonce, self.value, None)
        return {'id': self.id, 'value': (nonce + ciphertext).hex(), 'status': self.status}


class AsymmetricalKey(NamedTuple):
    """Named tuple representing a user's asymmetrical key with email, private key, and public key.

        Attributes:
            user_email: User's email address
            public_key: X25519 Public Key
            private_key: X25519 Private Key or None
        """
    user_email: str
    public_key: X25519PublicKey
    private_key: X25519PrivateKey

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(email={self.user_email}, '
                f'public_key={self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()} '
                f'private_key={self.private_key is not None})')

    @classmethod
    def new(cls, user_email: str | None = None) -> AsymmetricalKey:
        private_key: X25519PrivateKey = x25519.X25519PrivateKey.generate()
        public_key: X25519PublicKey = private_key.public_key()
        email: str = user_email or get_user_email()
        return cls(user_email=email, public_key=public_key, private_key=private_key)

    @classmethod
    def from_file(cls) -> AsymmetricalKey:
        if not private_key_file.exists():
            raise FileNotFoundError(f'Private key file {private_key_file} not found')
        with private_key_file.open('r') as f:
            user_email, private_hex = f.read().strip().split(maxsplit=1)
        assert user_email == get_user_email(), f'User email in {private_key_file} does not match git config'
        private_key = x25519.X25519PrivateKey.from_private_bytes(bytes.fromhex(private_hex))
        return cls(user_email=user_email, private_key=private_key, public_key=private_key.public_key())

    def to_file(self, key_file: Path = private_key_file) -> None:
        if key_file.exists():
            for i in range(8, 0, -1):
                old_backup = key_file.with_suffix(f'.{i}')
                new_backup = key_file.with_suffix(f'.{i + 1}')
                if old_backup.exists():
                    old_backup.rename(new_backup)
                    print(f'Backed up existing private key file {key_file} to {old_backup}')
            backup_file = key_file.with_suffix('.1')
            key_file.rename(backup_file)
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.parent.chmod(0o700)
        with key_file.open('w') as f:
            private_hex: str = self.private_key.private_bytes(encoding=Encoding.Raw,
                                                              format=PrivateFormat.Raw,
                                                              encryption_algorithm=NoEncryption()).hex()
            f.write(f'{self.user_email} {private_hex}\n')
            print(f'Private key file {key_file} initialized')
        get_user_key.cache_clear()
        _ = get_user_key()


class AsymmetricalPublicKey(NamedTuple):
    user_email: str
    public_key: X25519PublicKey

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> AsymmetricalPublicKey:
        if not _validate_email(email := data['email']):
            raise ValueError(f'Invalid email address: {email}')
        public_key: X25519PublicKey = X25519PublicKey.from_public_bytes(bytes.fromhex(data['public_key']))
        return cls(user_email=email, public_key=public_key)

    @classmethod
    def from_key_pair(cls, key_pair: AsymmetricalKey) -> AsymmetricalPublicKey:
        return cls(user_email=key_pair.user_email, public_key=key_pair.public_key)

    def as_dict(self, master_key: bytes | None = None) -> dict[str, str | None]:
        return {
            'email': self.user_email,
            'public_key': self.public_key.public_bytes(Encoding.Raw, PublicFormat.Raw).hex(),
            'master_key': lock(master_key, public_key=self.public_key) if master_key else None,
        }


@lru_cache(maxsize=None)
def get_user_email() -> str:
    """Get the user's email address from git config."""
    cmd = 'git config user.email'
    try:
        result = subprocess_run(cmd, shell=True, capture_output=True, check=True, text=True)
    except CalledProcessError as e:
        print(f'Failed to get user email: {e}')
        raise ValueError('Failed to get user email') from e
    email: str = result.stdout.strip()
    if not _validate_email(email):
        print(f'Invalid email address: {email}; use git config user.email <email> to set it')
        raise ValueError(f'Invalid email address: {email}')
    return email


def _validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return match(pattern, email) is not None


@lru_cache(maxsize=None)
@error_handler('get user key')
def get_user_key() -> AsymmetricalKey:
    user: AsymmetricalKey = AsymmetricalKey.from_file()
    assert user.private_key is not None, f'Private key not found in {private_key_file.name}'
    return user


@error_handler('lock aes key')
def lock(aes_master_key: bytes, /, *, public_key: X25519PublicKey) -> str:
    """ Encrypt the aes_key using the user's public key."""
    ephemeral: AsymmetricalKey = AsymmetricalKey.new()
    shared_secret: bytes = ephemeral.private_key.exchange(public_key)
    derived_key: bytes = HKDF(algorithm=SHA256(), length=32, salt=None, info=b'key-encryption').derive(shared_secret)
    cipher: ChaCha20Poly1305 = ChaCha20Poly1305(derived_key)
    nonce: bytes = b'\x00' * 12
    ciphertext: bytes = cipher.encrypt(nonce, aes_master_key, None)
    ephemeral_public_bytes: bytes = ephemeral.public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    return (ephemeral_public_bytes + ciphertext).hex()


@error_handler('unlock aes key')
def unlock(encrypted_aes_master_key: str, /, *, private_key: X25519PrivateKey) -> bytes:
    """ Decrypt the aes_key using the user's private key."""
    encrypted_bytes: bytes = bytes.fromhex(encrypted_aes_master_key)
    ephemeral_public_bytes: bytes = encrypted_bytes[:32]
    ciphertext: bytes = encrypted_bytes[32:]
    ephemeral_public: X25519PublicKey = x25519.X25519PublicKey.from_public_bytes(ephemeral_public_bytes)
    shared_secret: bytes = private_key.exchange(ephemeral_public)
    derived_key: bytes = HKDF(algorithm=SHA256(), length=32, salt=None, info=b'key-encryption').derive(shared_secret)
    cipher: ChaCha20Poly1305 = ChaCha20Poly1305(derived_key)
    nonce: bytes = b'\x00' * 12
    return cipher.decrypt(nonce, ciphertext, None)


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
    get_key.cache_clear()
    read_keys_file.cache_clear()
    _ = read_keys_file()


@lru_cache(maxsize=None)
@error_handler('get key')
def get_key(key_id: str | None = None) -> SymmetricalKey:
    user_key: AsymmetricalKey = get_user_key()
    data: dict[str, Any] = read_keys_file()
    user_data = next(raw_user for raw_user in data['users'] if raw_user['email'] == user_key.user_email)
    enc_master_key: str = user_data['master_key']
    assert enc_master_key is not None, f"Master key not found for user with email '{user_key.user_email}'"
    master_key: bytes = unlock(enc_master_key, private_key=user_key.private_key)
    if key_id is None:
        selected: dict[str, str] = choice([raw for raw in data['keys'] if raw['status'] == 'active'])
    else:
        selected = next(raw for raw in data['keys'] if raw['id'] == key_id)
    return SymmetricalKey.from_dict(selected, master_key)


def init_user_private_key_file() -> None:
    if private_key_file.exists():
        return
    user_email = get_user_email()
    AsymmetricalKey.new(user_email=user_email).to_file()


def rekey_keys_file(num_new_keys: int = 0) -> int:
    if get_user_email() != admin_user:
        print(f'only admin user {admin_user} should initialize keys file')
        return 1
    init_user_private_key_file()
    user_key: AsymmetricalKey = get_user_key()
    new_master_key: bytes = token_bytes(32)
    if keys_file.exists():
        data: dict[str, Any] = read_keys_file()
        user_data = next(raw_user for raw_user in data['users'] if raw_user['email'] == user_key.user_email)
        master_key: bytes = unlock(user_data['master_key'], private_key=user_key.private_key)
        for raw_key in data['keys']:
            raw_key['value'] = SymmetricalKey.from_dict(raw_key, master_key).as_dict(new_master_key)['value']
    else:
        backup_user_key = AsymmetricalKey.new(user_email=admin_user)
        backup_user_key.to_file(private_key_file.with_suffix('.backup'))
        data = {
            '$schema': schema_file.name,
            'version': keys_version,
            'users': [AsymmetricalPublicKey.from_key_pair(user_key).as_dict(new_master_key),
                      AsymmetricalPublicKey.from_key_pair(backup_user_key).as_dict(new_master_key)],
            'keys': [SymmetricalKey.new('active').as_dict(new_master_key) for _ in range(32)]
        }
    data['keys'].extend([SymmetricalKey.new('active').as_dict(new_master_key) for _ in range(num_new_keys)])
    for raw_user in data['users']:
        user_public_key = X25519PublicKey.from_public_bytes(bytes.fromhex(raw_user['public_key']))
        raw_user['master_key'] = lock(new_master_key, public_key=user_public_key)
    write_keys_file(data)
    return 0


def rekey_user_private_key_file() -> None:
    AsymmetricalKey.new(user_email=get_user_email()).to_file()


if __name__ == '__main__':
    rekey_keys_file(0)
