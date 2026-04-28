#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""AES-based symmetric encryption and decryption with key derivation."""
from __future__ import annotations

from secrets import token_bytes
from typing import Literal, cast
from typing import NamedTuple
from uuid import UUID, uuid7

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

__all__ = ['EncKey']


class EncKey(NamedTuple):
    """An AES-256-GCM symmetric encryption key with a UUID7 identifier and lifecycle status."""

    id: str
    value: bytes
    status: Literal['active', 'reserved', 'retired', 'unmanaged']

    def __str__(self) -> str:
        """Return a truncated, human-readable summary of the key id, value, and status."""
        return f'{self.__class__.__name__}(id=...{self.id[-8:]}, value={self.value.hex()[:8]}..., status={self.status})'

    @classmethod
    def new(cls, status: Literal['active', 'reserved', 'retired', 'unmanaged'] = 'unmanaged') -> EncKey:
        """Generate a new EncKey with a random 32-byte value and a UUID7 identifier."""
        value: bytes = token_bytes(32)
        return cls(id=uuid7().hex, value=value, status=status)

    @classmethod
    def from_dict(cls, key_id: str, data: dict[str, str], /, *, master_key: bytes) -> EncKey:
        """
        Deserialize and decrypt an EncKey from its keys.json representation.

        The stored value is AES-GCM ciphertext prefixed with a 12-byte nonce,
        encrypted under master_key.

        Args:
            key_id:     Hex UUID7 string used as the key identifier.
            data:       Dict with 'value' (hex nonce+ciphertext) and 'status' fields.
            master_key: 32-byte AES master key used to decrypt the stored key value.

        Returns:
            The decrypted EncKey.

        Raises:
            AssertionError: If key_id is not a UUID7, or the decrypted key is not 32 bytes.
        """
        assert UUID(hex=key_id).version == 7, f"key id '{key_id}' must be UUID version 7"
        value_bytes: bytes = bytes.fromhex(data['value'])
        nonce: bytes = value_bytes[:12]
        ciphertext: bytes = value_bytes[12:]
        key_bytes: bytes = AESGCM(master_key).decrypt(nonce, ciphertext, None)
        assert len(key_bytes) == 32, f"key '{key_id}' must be 32 bytes long"
        status = cast(Literal['active', 'reserved', 'retired', 'unmanaged'], data['status'])
        return cls(id=key_id, value=key_bytes, status=status)

    @classmethod
    def from_keys_data(cls, keys_data: dict[str, dict[str, str]], /, *, master_key: bytes) -> list[EncKey]:
        """Deserialize and decrypt all keys from the 'keys' section of keys.json."""
        return [cls.from_dict(key_id, key_data, master_key=master_key) for key_id, key_data in keys_data.items()]

    def as_dict(self, *, master_key: bytes) -> dict[str, str]:
        """
        Serialize this key to its keys.json representation, encrypting the value under master_key.

        Args:
            master_key: 32-byte AES master key used to encrypt this key's value.

        Returns:
            Dict with 'value' (hex nonce+ciphertext) and 'status' fields.
        """
        assert len(master_key) == 32, f'master_key must be 32 bytes long, got: {len(master_key)}'
        nonce: bytes = token_bytes(12)
        ciphertext: bytes = AESGCM(master_key).encrypt(nonce, self.value, None)
        return {'value': (nonce + ciphertext).hex(), 'status': self.status}

    def __aad(self, aad: bytes | None = None) -> bytes:
        if aad is None:
            return bytes.fromhex(self.id)
        if not isinstance(aad, bytes):
            raise TypeError(f'aad must be bytes or None, got: {aad.__class__.__name__}')
        return aad

    def decrypt(self, cypher_text: bytes, /, *, aad: bytes | None = None) -> bytes:
        """
        Decrypt AES-GCM ciphertext produced by encrypt().

        The expected wire format is: 16-byte key ID | 12-byte nonce | ciphertext+tag.

        Args:
            cypher_text: Bytes in the wire format written by encrypt().
            aad:         Additional authenticated data; defaults to the key ID bytes when None.

        Returns:
            The decrypted plaintext bytes.

        Raises:
            ValueError: If cypher_text is not in the expected wire format.
        """
        try:
            nonce: bytes = cypher_text[16:28]
            ciphertext: bytes = cypher_text[28:]
            return AESGCM(self.value).decrypt(nonce, ciphertext, self.__aad(aad))
        except Exception as e:
            raise ValueError('Failed to decrypt') from e

    def encrypt(self, plain_text: bytes, /, *, aad: bytes | None = None) -> bytes:
        """
        Encrypt plaintext with AES-256-GCM and prepend the key ID and nonce.

        Wire format: 16-byte key ID | 12-byte nonce | ciphertext+tag.

        Args:
            plain_text: Bytes to encrypt.
            aad:        Additional authenticated data; defaults to the key ID bytes when None.

        Returns:
            The encrypted payload in wire format.
        """
        nonce: bytes = token_bytes(12)
        ciphertext: bytes = AESGCM(self.value).encrypt(nonce, plain_text, self.__aad(aad))
        return bytes.fromhex(self.id) + nonce + ciphertext  # 16 bytes key id + 12 bytes nonce + ciphertext
