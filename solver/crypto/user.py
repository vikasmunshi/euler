#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

import subprocess
from functools import lru_cache
from json import dumps, loads
from pathlib import Path
from re import match
from typing import NamedTuple

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import (X25519PrivateKey as PrivateKey,
                                                              X25519PublicKey as PublicKey)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

from solver.workspace import BASE_DIR

__all__ = ['UserIdentity', 'get_user', 'lock', 'unlock']

_private_key_file: Path = BASE_DIR / 'keys' / 'id_x25519.json'


class UserIdentity(NamedTuple):
    """Named tuple representing a user's asymmetrical key with email, private key, and public key.

        Attributes:
            email: User's email address
            public_key: X25519 Public Key
            private_key: X25519 Private Key or None
            algorithm: Key algorithm, default is 'x25519'
        """
    email: str
    public_key: PublicKey
    private_key: PrivateKey | None = None
    algorithm: str = 'x25519'

    @property
    def private_key_str(self) -> str | None:
        return self.private_key.private_bytes(encoding=Encoding.Raw,
                                              format=PrivateFormat.Raw,
                                              encryption_algorithm=NoEncryption(),
                                              ).hex() if self.private_key is not None else None

    @property
    def public_key_str(self) -> str:
        return self.public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw, ).hex()

    def __repr__(self) -> str:
        return (f'AsymmetricalKey(email={self.email}, '
                f'private_key={self.private_key_str}, public_key={self.public_key_str})')

    @classmethod
    def new(cls) -> UserIdentity:
        private_key: PrivateKey = x25519.X25519PrivateKey.generate()
        public_key: PublicKey = private_key.public_key()
        return cls(algorithm='x25519', email=_get_user_email(), private_key=private_key, public_key=public_key)

    @classmethod
    def from_dict(cls, data: dict[str, ...]) -> UserIdentity:
        if 'algorithm' not in data:
            data['algorithm'] = 'x25519'
        if data['algorithm'] != 'x25519':
            raise NotImplementedError(f'Unsupported key algorithm: {data["algorithm"]}')
        if not _validate_email(email := data['email']):
            raise ValueError(f'Invalid email address: {email}')
        if 'private_key' not in data:
            private_key: PrivateKey | None = None
        else:
            private_key = x25519.X25519PrivateKey.from_private_bytes(bytes.fromhex(data['private_key']))
        public_key: PublicKey = x25519.X25519PublicKey.from_public_bytes(bytes.fromhex(data['public_key']))
        return cls(algorithm=data['algorithm'], email=email, private_key=private_key, public_key=public_key)

    @classmethod
    def load(cls) -> UserIdentity:
        try:
            instance = cls.from_dict(loads(_private_key_file.read_text()))
        except (KeyError, ValueError, NotImplementedError, FileNotFoundError):
            email: str = _get_user_email()
            private_key: PrivateKey = x25519.X25519PrivateKey.generate()
            public_key: PublicKey = private_key.public_key()
            instance: UserIdentity = cls(algorithm='x25519',
                                         email=email,
                                         private_key=private_key,
                                         public_key=public_key)
            _private_key_file.parent.mkdir(parents=True, exist_ok=True)
            _private_key_file.write_text(dumps(instance.as_dict(), indent=2))
            _private_key_file.chmod(0o600)
            print(f'Created new private key file: {_private_key_file}')
        return instance

    def as_dict(self) -> dict[str, ...]:
        return {'algorithm': self.algorithm,
                'email': self.email,
                'private_key': self.private_key_str,
                'public_key': self.public_key_str}


@lru_cache(maxsize=None)
def _get_user_email() -> str:
    """Get the user's email address from git config."""
    cmd = 'git config user.email'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f'Failed to get user email: {e}')
        raise
    email: str = result.stdout.strip()
    if not _validate_email(email):
        raise ValueError(f'Invalid email address: {email}')
    return email


def _validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return match(pattern, email) is not None


@lru_cache(maxsize=None)
def get_user() -> UserIdentity:
    return UserIdentity.load()


def lock(aes_master_key: bytes, /, *, user_key: UserIdentity = None) -> str:
    """ Encrypt the aes_key using the user's public key."""
    if user_key is None:
        user_key = get_user()
    ephemeral: UserIdentity = UserIdentity.new()
    shared_secret: bytes = ephemeral.private_key.exchange(user_key.public_key)
    derived_key: bytes = HKDF(algorithm=SHA256(), length=32, salt=None, info=b'key-encryption').derive(shared_secret)
    cipher: ChaCha20Poly1305 = ChaCha20Poly1305(derived_key)
    nonce = b'\x00' * 12
    ciphertext: bytes = cipher.encrypt(nonce, aes_master_key, None)
    ephemeral_public_bytes: bytes = ephemeral.public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    return (ephemeral_public_bytes + ciphertext).hex()


def unlock(encrypted_aes_master_key: str, /, ) -> bytes:
    """ Decrypt the aes_key using the user's private key."""
    user_key: UserIdentity = get_user()
    encrypted_bytes: bytes = bytes.fromhex(encrypted_aes_master_key)
    ephemeral_public_bytes: bytes = encrypted_bytes[:32]
    ciphertext: bytes = encrypted_bytes[32:]
    ephemeral_public = x25519.X25519PublicKey.from_public_bytes(ephemeral_public_bytes)
    shared_secret: bytes = user_key.private_key.exchange(ephemeral_public)
    derived_key: bytes = HKDF(algorithm=SHA256(), length=32, salt=None, info=b'key-encryption').derive(shared_secret)
    cipher: ChaCha20Poly1305 = ChaCha20Poly1305(derived_key)
    nonce = b'\x00' * 12
    aes_key = cipher.decrypt(nonce, ciphertext, None)
    return aes_key
