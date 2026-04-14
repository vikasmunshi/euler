#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from secrets import token_bytes
from uuid import uuid7

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from solver.crypto.error import error_handler
from solver.crypto.keys import SymmetricalKey, get_key

__all__ = ['decrypt', 'encrypt']


@error_handler('decrypt cipher_text bytes')
def decrypt(cypher_text: bytes, /, *, key: bytes | SymmetricalKey | None = None, aad: bytes | None = None) -> bytes:
    if key is None:
        _key: SymmetricalKey = get_key(cypher_text[0:16].hex())
    elif isinstance(key, bytes):
        _key = SymmetricalKey(id=cypher_text[0:16].hex(), value=key, status='unmanaged')
    else:
        _key = key
    if not isinstance(_key, SymmetricalKey):
        raise TypeError(f'key must be bytes or Key or None, got: {_key.__class__.__name__}')
    if aad is None:
        aad = bytes.fromhex(_key.id)
    elif not isinstance(aad, bytes):
        raise TypeError(f'aad must be bytes or None, got: {aad.__class__.__name__}')
    nonce: bytes = cypher_text[16:28]
    ciphertext: bytes = cypher_text[28:]
    return AESGCM(_key.value).decrypt(nonce, ciphertext, aad)


@error_handler('encrypt plain_text bytes')
def encrypt(plain_text: bytes, /, *, key: bytes | SymmetricalKey | None = None, aad: bytes | None = None) -> bytes:
    if key is None:
        _key: SymmetricalKey = get_key()
    elif isinstance(key, bytes):
        _key = SymmetricalKey(id=uuid7().hex, value=key, status='unmanaged')
    else:
        _key = key
    if not isinstance(_key, SymmetricalKey):
        raise TypeError(f'key must be bytes or Key or None, got: {_key.__class__.__name__}')
    if aad is None:
        aad = bytes.fromhex(_key.id)
    elif not isinstance(aad, bytes):
        raise TypeError('aad must be bytes')
    nonce: bytes = token_bytes(12)
    ciphertext: bytes = AESGCM(_key.value).encrypt(nonce, plain_text, aad)
    return bytes.fromhex(_key.id) + nonce + ciphertext  # 16 bytes key id + 12 bytes nonce + ciphertext
