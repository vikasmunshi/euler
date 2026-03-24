#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

__all__ = ['encrypt', 'decrypt']

from functools import wraps
from pathlib import Path
from secrets import token_bytes
from uuid import uuid7

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from solver.crypto.keys import Key, get_default_key, get_key


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
def encrypt(plain_text: bytes, /, *, key: bytes | Key = None, aad: bytes = None) -> bytes:
    if key is None:
        key = get_default_key()
    elif isinstance(key, bytes):
        key = Key(id=uuid7().hex, value=key, status='unmanaged')
    elif not isinstance(key, Key):
        raise TypeError('key must be bytes or Key')
    if aad is None:
        aad = bytes.fromhex(key.id)
    elif not isinstance(aad, bytes):
        raise TypeError('aad must be bytes')
    nonce: bytes = token_bytes(12)
    ciphertext: bytes = AESGCM(key.value).encrypt(nonce, plain_text, aad)
    return bytes.fromhex(key.id) + nonce + ciphertext  # 16 bytes key id + 12 bytes nonce + ciphertext


@_handle_crypto_exceptions('decrypt')
def decrypt(cypher_text: bytes, /, *, key: bytes | Key = None, aad: bytes = None) -> bytes:
    if key is None:
        key = get_key(key_id=cypher_text[0:16].hex())
    elif isinstance(key, bytes):
        key = Key(id=cypher_text[0:16].hex(), value=key, status='unmanaged')
    elif not isinstance(key, Key):
        raise TypeError('key must be bytes or Key')
    if aad is None:
        aad = bytes.fromhex(key.id)
    elif not isinstance(aad, bytes):
        raise TypeError('aad must be bytes')
    nonce: bytes = cypher_text[16:28]
    ciphertext: bytes = cypher_text[28:]
    return AESGCM(key.value).decrypt(nonce, ciphertext, aad)


if __name__ == '__main__':
    for _key in (None, token_bytes(32)):
        _plain_text: bytes = (Path(__file__).parent / 'constants').read_bytes()
        _cipher_text: bytes = encrypt(_plain_text, key=_key)
        _decrypted_text: bytes = decrypt(_cipher_text, key=_key)
        try:
            _ = decrypt(_cipher_text, key=None)
        except ValueError:
            pass
        print(_plain_text == _decrypted_text)
