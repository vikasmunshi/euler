#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Cryptographic key management: user identity, master key access, and stack re-encryption."""
from __future__ import annotations

from json import dumps
from typing import Any

from solver.config import ColorCodes, private_key_file, root_dir

__all__ = ['rekey', 'user']


def rekey(num_total_active_keys: int = 32, /, *, preserve_master: bool = True, backup: bool = False) -> None:
    """
    Reinitialize keys.json with additional new encryption keys.

    Generates enough new active keys to reach num_total_active_keys in total,
    optionally re-encrypting them under a new master key. Only accessible to admin users.

    Args:
        num_total_active_keys: Target number of active keys in keys.json after rekeying. Defaults to 32.
        preserve_master:       If True, retain the existing master key; if False, generate a new one.
                               Defaults to True.
        backup:                If True, print the backup keys for offline vault. Defaults to False.
    """
    from solver.crypto.keys import rekey_keys_file

    rekey_keys_file(num_total_active_keys, preserve_master=preserve_master)

    if backup:
        from solver.crypto.keys import get_user_key, read_keys_file
        from solver.utils import write_file

        lines: dict[str, str] = {
            'private_key': private_key_file.read_text().strip(),
            **read_keys_file()['users'][get_user_key().user_email]
        }
        write_file(root_dir / 'backup/keys_backup.json', dumps(lines, indent=4).encode(), msg='keys backup')


def user(regen: bool = False) -> str:
    """
    Return the current user's identity alongside their master key access.

    Loads the X25519 private key from ~/.ssh/id_solver. If no private key exists there,
    or if regen is True, a new X25519 key pair is generated and the private key is persisted
    to ~/.ssh/id_solver. When a new key pair is generated, the corresponding public key entry
    is written to <repo>/keys/keys.json under the user's email:

        data['users'][user_key.user_email] = {
            "public_key": user_key.public_key.to_public_bytes().hex(),
            "master_key": user_key.lock(master_key) or None,
        }

    Run `solver upload_keys` to create a pull request with the updated keys/keys.json;
    the administrator will then add the encrypted master key for the new user.

    Note: generating a new key pair requires the GitHub CLI (gh) to be authenticated (gh auth login).

    Args:
        regen: If True, generate and persist a new key pair regardless of whether one already
               exists at ~/.ssh/id_solver. Defaults to False.

    Returns:
        A colour-coded string identifying the user and indicating whether they have
        access to the master key (✓ can encrypt/decrypt in green, ✗ cannot in red).
    """
    from solver.crypto.asymmetrical import UserKeyPair
    from solver.crypto.keys import get_master_key, get_user_key, read_keys_file, write_keys_file

    try:
        user_key: UserKeyPair | None = get_user_key()
    except (AssertionError, FileNotFoundError):
        user_key = None
    try:
        master_key: bytes | None = get_master_key()
    except (AssertionError, FileNotFoundError):
        master_key = None
    if regen or user_key is None:
        user_key = UserKeyPair.new_persistent()
        get_user_key.cache_clear()
        data: dict[str, Any] = read_keys_file()
        data['users'][user_key.user_email] = user_key.to_public_dict(master_key)
        write_keys_file(data)
    return (f'{user_key!s} '
            f'{(ColorCodes.RED + "(✗ cannot") if master_key is None else (ColorCodes.GREEN + "(✓ can")} '
            f'encrypt/decrypt){ColorCodes.RESET}')
