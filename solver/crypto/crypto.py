#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from secrets import token_bytes
from uuid import uuid7

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from solver.crypto.error import error_handler
from solver.crypto.keys import SymmetricalKey, get_key, get_key

__all__ = ['decrypt', 'encrypt']


@error_handler('encrypt plain_text bytes')
def encrypt(plain_text: bytes, /, *, key: bytes | SymmetricalKey | None = None, aad: bytes | None = None) -> bytes:
    if key is None:
        key = get_key()
    elif isinstance(key, bytes):
        key = SymmetricalKey(id=uuid7().hex, value=key, status='unmanaged')
    elif not isinstance(key, SymmetricalKey):
        raise TypeError('key must be bytes or Key')
    if aad is None:
        aad = bytes.fromhex(key.id)
    elif not isinstance(aad, bytes):
        raise TypeError('aad must be bytes')
    nonce: bytes = token_bytes(12)
    ciphertext: bytes = AESGCM(key.value).encrypt(nonce, plain_text, aad)
    return bytes.fromhex(key.id) + nonce + ciphertext  # 16 bytes key id + 12 bytes nonce + ciphertext


@error_handler('decrypt cipher_text bytes')
def decrypt(cypher_text: bytes, /, *, key: bytes | SymmetricalKey | None = None, aad: bytes | None = None) -> bytes:
    if key is None:
        key = get_key(cypher_text[0:16].hex())
    elif isinstance(key, bytes):
        key = SymmetricalKey(id=cypher_text[0:16].hex(), value=key, status='unmanaged')
    elif not isinstance(key, SymmetricalKey):
        raise TypeError('key must be bytes or Key')
    if aad is None:
        aad = bytes.fromhex(key.id)
    elif not isinstance(aad, bytes):
        raise TypeError('aad must be bytes')
    nonce: bytes = cypher_text[16:28]
    ciphertext: bytes = cypher_text[28:]
    return AESGCM(key.value).decrypt(nonce, ciphertext, aad)
