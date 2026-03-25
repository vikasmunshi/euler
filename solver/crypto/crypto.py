#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import wraps
from pathlib import Path
from secrets import token_bytes
from uuid import uuid7

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from solver.crypto.keys import SymmetricalKey, get_default_key, get_key

__all__ = ['encrypt', 'decrypt', 'default_key_is_valid']


def _handle_crypto_exceptions(operation: str):
    """Decorator to handle exceptions in encrypt/decrypt operations."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError as e:
                key_id = args[0][0:16].hex() if operation == 'decrypt' and args else 'unknown'
                msg = (f'{operation.capitalize()} failed: Key {key_id} not found in vault.\n'
                       f'       The key may have been retired and deleted, or\n'
                       f'       the ciphertext was created using encrypt(plain_text, key=<bytes>).')
                print(f'Error: {msg}')
                raise ValueError(msg) from e
            except (TypeError, AttributeError) as e:
                msg = f'{operation.capitalize()} failed: Invalid input type. Expected bytes or Key object.'
                print(f'Error: {msg}')
                raise ValueError(msg) from e
            except ValueError as e:
                if 'must be bytes' in str(e).lower():
                    raise
                msg = f'{operation.capitalize()} failed: {str(e)}'
                print(f'Error: {msg}')
                raise ValueError(msg) from e
            except Exception as e:
                msg = f'{operation.capitalize()} failed: {type(e).__name__}: {str(e)}'
                print(f'Error: {msg}')
                raise ValueError(msg) from e

        return wrapper

    return decorator


@_handle_crypto_exceptions('encrypt')
def encrypt(plain_text: bytes, /, *, key: bytes | SymmetricalKey = None, aad: bytes = None) -> bytes:
    if key is None:
        key = get_default_key()
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


@_handle_crypto_exceptions('decrypt')
def decrypt(cypher_text: bytes, /, *, key: bytes | SymmetricalKey = None, aad: bytes = None) -> bytes:
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


def default_key_is_valid() -> bool:
    # noinspection PyBroadException
    try:
        get_default_key()
    except:
        return False
    else:
        plain_text: bytes = (Path(__file__).parent / 'text_plain.txt').read_bytes()
        cipher_text: str = ''.join((Path(__file__).parent / 'text_cipher.txt').read_text().splitlines())
        decrypted_text: bytes = decrypt(bytes.fromhex(cipher_text))
        return plain_text == decrypted_text
