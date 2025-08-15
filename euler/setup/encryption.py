#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution encryption utility for private Project Euler problems."""
from __future__ import annotations

import base64
import hashlib
from os import getenv
from pathlib import Path
from typing import cast

import Crypto
import Crypto.Cipher.AES
import Crypto.Hash.SHA256
import Crypto.Util.Padding

from euler.logger import logger
from euler.setup.paths import get_module_path
from euler.utils.file_lock import FileLock


def derive_key(key: str) -> bytes:
    return hashlib.sha256(key.encode()).digest()


def encrypt_solution_module(euler_problem: int) -> None:
    py_file_path: Path = get_module_path(euler_problem)
    enc_file_path: Path = py_file_path.with_suffix('.enc')
    if py_file_path.exists():
        key: str | None = getenv('EULER_ENCRYPTION_KEY')
        if not key:
            raise RuntimeError('Missing EULER_ENCRYPTION_KEY')
        with FileLock(py_file_path, 'read') as f:
            source_code: str = f.read()
        enc_source_code: str = encrypt(source_code, key=key)
        with FileLock(enc_file_path, 'write') as f:
            f.write(enc_source_code)


def decrypt_solution_module(euler_problem: int) -> None:
    py_file_path: Path = get_module_path(euler_problem)
    enc_file_path: Path = py_file_path.with_suffix('.enc')
    if py_file_path.exists():
        from datetime import datetime
        timestamped_bak = py_file_path.with_suffix(f".bak.{datetime.now().isoformat()}")
        py_file_path.rename(timestamped_bak)
        logger.info(f"Backup created: {timestamped_bak}")
    if enc_file_path.exists():
        key: str | None = getenv('EULER_ENCRYPTION_KEY')
        if not key:
            raise RuntimeError('Missing EULER_ENCRYPTION_KEY')
        with FileLock(enc_file_path, 'read') as f:
            enc_source_code: str = f.read()
        source_code: str = decrypt(enc_source_code, key=key)
        with FileLock(py_file_path, 'write') as f:
            f.write(source_code)


def encrypt(plain_text: str, *, key: str) -> str:
    bytes_key: bytes = derive_key(key)
    cipher = Crypto.Cipher.AES.new(bytes_key, Crypto.Cipher.AES.MODE_CBC)
    cipher_text = cipher.encrypt(Crypto.Util.Padding.pad(plain_text.encode(), Crypto.Cipher.AES.block_size))
    return base64.b64encode(cast(bytes, cipher.iv) + cipher_text).decode()


def decrypt(cypher_text: str, *, key: str) -> str:
    bytes_key: bytes = derive_key(key)
    try:
        cypher_text_bytes = base64.b64decode(cypher_text)
        iv = cypher_text_bytes[:Crypto.Cipher.AES.block_size]
        cipher = Crypto.Cipher.AES.new(bytes_key, Crypto.Cipher.AES.MODE_CBC, iv=iv)
        return Crypto.Util.Padding.unpad(cipher.decrypt(cypher_text_bytes[Crypto.Cipher.AES.block_size:]),
                                         Crypto.Cipher.AES.block_size).decode()
    except Exception as err:
        logger.error(f"Decryption failed: {err}")
        raise ValueError("Decryption error: Invalid key or corrupted ciphertext.") from err
