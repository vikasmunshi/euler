#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Vault module for AES-256 encryption/decryption of sensitive Project Euler content.

This module provides cryptographic functions to protect private Project Euler problems
(101+) from being stored in plaintext. It uses AES-256 encryption in CBC mode with
automatic key generation and management.

Security Features:
    - AES-256 encryption (256-bit keys)
    - CBC (Cipher Block Chaining) mode for semantic security
    - Random IV (Initialization Vector) for each encryption operation
    - PKCS#7 padding for block alignment
    - Automatic key generation using cryptographically secure random numbers
    - Base64 encoding for text-safe storage

Key Management:
    - Keys are automatically generated on first use
    - Stored in keys/key.txt (already in .gitignore)
    - Key derived from SHA-256 hash of key file content
    - Multiple random hex tokens used as key material

Module Constants:
    KEY_FILE: Path to the encryption key file (keys/key.txt)
    KEY_SIZE: Size of the encryption key in bytes (32 = 256 bits)

Functions:
    encrypt: Encrypt plaintext using AES-256-CBC
    decrypt: Decrypt ciphertext using AES-256-CBC

Dependencies:
    pycryptodome: pip install pycryptodome

Example:
    >>> from solver.vault import decrypt, encrypt
    >>> plaintext = b"Secret problem content"
    >>> ciphertext = encrypt(plaintext)
    >>> decrypt(ciphertext) == plaintext
    True

Security Notes:
    - keys/key.txt is protected by .gitignore (will not be committed)
    - Loss of the key file means encrypted data cannot be recovered
    - Same plaintext encrypts to different ciphertext each time (random IV)
    - This provides confidentiality but not authentication (no MAC/HMAC)
    - Backup keys/key.txt securely if protecting important data
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from secrets import token_hex

import Crypto  # pip install pycryptodome
import Crypto.Cipher.AES
import Crypto.Hash.SHA256
import Crypto.Util.Padding

__all__ = ['encrypt', 'decrypt']

# File paths and key size
KEY_FILE: Path = Path.cwd() / 'keys' / 'key.txt'  # Main encryption key file
KEY_SIZE: int = 32  # AES-256 requires 32 bytes (256 bits)


@lru_cache()
def _get_key(*, key_file: Path = KEY_FILE, key_size: int = KEY_SIZE, genkey: bool = False) -> bytes:
    """Retrieve or generate the encryption key for AES-256 operations.

    Internal function that reads the encryption key from the key file. If the key file
    doesn't exist, behavior depends on the genkey parameter:
    - If genkey=True: Generates a new key automatically
    - If genkey=False (default): Raises FileNotFoundError

    The actual encryption key is derived by taking the SHA-256 hash of the key
    file content, ensuring a uniform 256-bit output regardless of the key material.

    The function is cached to avoid repeated file I/O operations during a session.

    Args:
        key_file: Path to the key file. Defaults to KEY_FILE (keys/key.txt).
        key_size: Size in bytes for each random hex token. Defaults to KEY_SIZE (32).
                 Note: The final key is always 32 bytes (SHA-256 output).
        genkey: If True, it automatically generates a new key file if it doesn't exist.
               If False, it raises FileNotFoundError when the key file is missing.
               Defaults to False (strict mode - requires key to exist).

    Returns:
        bytes: A 32-byte (256-bit) encryption key suitable for AES-256.

    Raises:
        FileNotFoundError: If key_file doesn't exist and genkey=False.
        PermissionError: If unable to create the key directory or write the key file.
        OSError: If unable to read the key file.

    Side Effects:
        - Creates the key directory if it doesn't exist (when genkey=True)
        - Generates and writes a new key file on first use (when genkey=True)
        - Prints status messages about key generation or usage

    Note:
        This is an internal function (prefixed with underscore) and should not be
        imported or used outside this module. Use encrypt() and decrypt() functions
        which automatically call this function to retrieve the key.

    Security Notes:
        - The key file contains 4 lines of random hex tokens for added entropy.
        - Each token is 32 bytes (64 hex chars) of cryptographically secure random data.
        - Final key derived via SHA-256 ensures uniform 256-bit output.
        - Key is cached in memory for the session duration.
        - The key file is protected by .gitignore (will not be committed to git).
        - Default genkey=False prevents accidental key generation in production.
        - Use genkey=True only during initial setup or in development.

    Note:
        Loss of the key file means all encrypted data becomes unrecoverable.
        Ensure proper backups of keys/key.txt if protecting important data.
        The default genkey=False is production-safe and prevents accidental
        key generation. Only use genkey=True when you intend to create a new key.
    """
    if not key_file.exists():
        if not genkey:
            raise FileNotFoundError(
                f'Encryption key not found at {key_file.as_posix()}. '
                f'Contact the project maintainer for the encryption key.')
        new_key: str = '\n'.join(token_hex(key_size) for _ in range(16))
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_text(new_key)
        print(f'Generated new encryption key and saved it to {key_file.as_posix()}')
        _verify_key(key=sha256(new_key.encode()).digest(), is_new_key=True)
    else:
        print(f'Using existing encryption key from {key_file.as_posix()}')
    key: bytes = sha256(key_file.read_text().encode()).digest()
    assert _verify_key(key=key), (
        f'Invalid encryption key in {key_file.as_posix()}. '
        f'Contact the project maintainer for the encryption key.'
    )
    return key


def _verify_key(*, key: bytes, is_new_key: bool = False) -> bool:
    """Validate that the encryption key is correct by testing encryption/decryption.

    Internal function used to verify key integrity and correctness. Tests the provided
    key by attempting to decrypt a known ciphertext and comparing it against the
    expected plaintext.

    The test uses the opening stanza of William Blake's "Auguries of Innocence"
    as the known plaintext, encrypted with the correct key.

    Args:
        key: Encryption key to validate. Must be exactly 32 bytes for AES-256.

    Returns:
        bool: True if the key successfully decrypts the test ciphertext to the
              expected plaintext, False otherwise (including if any exception occurs).

    Note:
        This is an internal function (prefixed with underscore) and should not be
        imported or used outside this module. It catches all exceptions and returns
        False instead of raising them, making it safe for internal validation.
    """
    plain_text: bytes = (
        b'To see a World in a Grain of Sand'
        b'And a Heaven in a Wild Flower'
        b'Hold Infinity in the palm of your hand'
        b'And Eternity in an hour'
    )
    if is_new_key:
        cipher_text: bytes = encrypt(plain_text, key=key)
        print('New cipher text:', cipher_text.decode(), sep='\n')
    else:
        # noinspection SpellCheckingInspection
        cipher_text = (
            rb'2T6wBeZ+yF9BR6NgVcWH0DRVEjTsurbPM+o+0y+6eTBNQ5n4Y7tDE7+zPqjprhVw2PAti/c93FNt6tx3Nf+IldauCsDxmZwy'
            rb'd0PnUcGtWSb2h7DffZCmF4vt5B4ep7gZJaaS7IVcs5DEQ1Au8h+pgPqd6ardNIGYpPBzf0IhMAiR87TJD9UidYAdaZNEJ35T'
        )
    # noinspection PyBroadException
    try:
        return decrypt(cipher_text, key=key) == plain_text
    except Exception:
        return False


def decrypt(cypher_text: bytes, *, key: bytes = None) -> bytes:
    """Decrypt ciphertext that was encrypted using AES-256 in CBC mode.

    Decrypts a base64-encoded ciphertext bytes produced by the encrypt()
    function. Extracts the IV from the beginning of the decoded data, then uses it
    to decrypt the remaining ciphertext and remove padding.

    Args:
        cypher_text: Base64-encoded bytes containing IV + encrypted data.
                     Must be in the format produced by encrypt().
        key: Optional decryption key. If None, use the default key from keys/key.txt.
             Must be exactly 32 bytes for AES-256 and match the encryption key.
             Defaults to None.

    Returns:
        bytes: The decrypted plaintext bytes.

    Raises:
        ValueError: If the ciphertext is malformed, padding is invalid, or
                    base64 decoding fails.

    Examples:
        >>> plaintext = b'Secret message'
        >>> ciphertext = encrypt(plaintext)
        >>> decrypt(ciphertext) == plaintext
        True
        >>> decrypt(ciphertext)
        b'Secret message'

    Technical Details:
        - Algorithm: AES-256-CBC
        - Padding removal: PKCS#7 (automatic via Crypto.Util.Padding)
        - IV extraction: First 16 bytes of decoded data
        - Block size: 16 bytes (128 bits)
        - Encoding: Base64 decoded before decryption

    Note:
        The decryption will fail if:
        - Wrong key is used
        - Ciphertext has been modified or corrupted
        - Input is not properly base64-encoded
        - Padding is invalid
    """
    key = key or _get_key()
    decoded_cypher_text = b64decode(cypher_text)
    iv = decoded_cypher_text[:Crypto.Cipher.AES.block_size]
    cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC, iv=iv)
    plain_text = cipher.decrypt(decoded_cypher_text[Crypto.Cipher.AES.block_size:])
    return Crypto.Util.Padding.unpad(plain_text, Crypto.Cipher.AES.block_size)


def encrypt(plain_text: bytes, *, key: bytes = None) -> bytes:
    """Encrypt plaintext using AES-256 in CBC mode.

    Encrypts the input bytes using AES-256 encryption with a randomly generated
    Initialization Vector (IV) for each encryption operation. The IV is prepended
    to the ciphertext, and the result is base64-encoded for text-safe storage.

    The same plaintext will produce different ciphertext each time due to the
    random IV, providing semantic security.

    Args:
        plain_text: The plaintext bytes to encrypt.
        key: Optional encryption key. If None, use the default key from keys/key.txt.
             Must be exactly 32 bytes for AES-256. Defaults to None.

    Returns:
        bytes: Base64-encoded bytes containing IV + ciphertext.
               Format: base64(IV || encrypted_data)
               Safe for storage in text files.

    Examples:
        >>> plaintext = b"Secret message"
        >>> encrypted1 = encrypt(plaintext)
        >>> encrypted2 = encrypt(plaintext)
        >>> encrypted1 != encrypted2  # Different due to random IV
        True
        >>> len(encrypted1) > len(plaintext)  # Longer due to encoding/padding
        True

    Technical Details:
        - Algorithm: AES-256-CBC
        - Padding: PKCS#7 (automatic via Crypto.Util.Padding)
        - IV: 16 bytes (128 bits), randomly generated per encryption
        - Block size: 16 bytes (128 bits)
        - Encoding: Base64 for text compatibility

    Note:
        The IV must be unique for each encryption with the same key to maintain
        security. This function automatically handles IV generation.
    """
    key = key or _get_key()
    cipher = Crypto.Cipher.AES.new(key, Crypto.Cipher.AES.MODE_CBC)
    cipher_text = cipher.encrypt(Crypto.Util.Padding.pad(plain_text, Crypto.Cipher.AES.block_size))
    return b64encode(cipher.iv + cipher_text)


if __name__ == '__main__':
    # _ = _get_key(genkey=True)
    raise SystemExit(0 if _verify_key(key=_get_key()) else 1)
