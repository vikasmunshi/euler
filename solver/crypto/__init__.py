#! /usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Cryptographic key management: user identity, master key access, and stack re-encryption."""
from __future__ import annotations

from json import dumps
from typing import Any, NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    from solver.crypto.asymmetrical import UserKeyPair

from solver.config import root_dir

__all__ = ['rekey', 'user']


class User(NamedTuple):
    """Represents a user with a public and private key pair."""
    user_key: UserKeyPair
    master_key: bytes | None

    def __str__(self) -> str:
        """Return a label showing the user key and whether the master key is available."""
        return f'{self.user_key!s} ({"✗ cannot" if self.master_key is None else "✓ can"} encrypt/decrypt)'


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
        from solver.crypto.asymmetrical import private_key_file
        from solver.crypto.keys import get_user_key, read_keys_file
        from solver.utils import write_file

        lines: dict[str, str] = {
            'private_key': private_key_file.read_text().strip(),
            **read_keys_file()['users'][get_user_key().user_email]
        }
        write_file(root_dir / 'backup/keys_backup.json', dumps(lines, indent=4).encode(), msg='keys backup')


def user(regen: bool = False) -> User:
    """
    Return the current user's identity alongside their master key access.

    Loads the user's key pair from disk and attempts to decrypt the master key.
    If no key pair exists on disk, or if regen is True, a new persistent key pair
    is generated and registered in keys.json.

    Args:
        regen: If True, generate and persist a new key pair regardless of whether one already exists.
               Defaults to False.

    Returns:
        A User named tuple containing the UserKeyPair and the decrypted master key
        (or None if the master key is not accessible to this user).
    """
    from solver.crypto.asymmetrical import UserKeyPair
    from solver.crypto.keys import get_master_key, get_user_key, read_keys_file, write_keys_file

    try:
        user_key: UserKeyPair = get_user_key()
    except (AssertionError, FileNotFoundError):
        user_key = None  # type: ignore [assignment]
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
    return User(user_key, master_key)
