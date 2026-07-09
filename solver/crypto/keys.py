#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Cipher key management: create, persist, rotate and share the crypto key material.

This is the **interactive** half of `solver.crypto` -- all user interaction (password prompts, share
entry, confirmations) lives here, and nowhere else. It owns the lifecycle of two keys:

- The **asymmetric** identity: an X25519 key pair. The private key is generated here and written
  **plain** (unencrypted PKCS8 PEM) to `~/.euler/id` -- a machine-local `0600` file outside the
  repo, whose file permissions are its protection -- so the non-interactive load path
  (`solver.crypto.ciphers.load_private_key`) needs no password.
- The **symmetric** master key: a single 32-byte AES key, wrapped to each authorised user's public
  key in `keys/enc-key.json` -- a `{<public-key-hex>: <locked-master-key-hex>}` map plus a `verify`
  ciphertext. Authority is **proof-of-possession**: anyone who can unwrap and verify the current
  master key may rotate it, authorise another public key, or split it into shares.

The non-interactive primitives (load, lock/unlock, encrypt/decrypt) come from `solver.crypto.ciphers`
and the configuration from `solver.crypto.config`; this module never re-implements them. The git
filter (`solver.crypto.gitfilter`) does not import this module.

Shell commands registered here: `user`, `rekey`, `authorize`, `key-split`, `key-reconstruct`.
"""
from __future__ import annotations

__all__ = ['key_reconstruct', 'key_rekey', 'key_split', 'user', 'user_authorize']

from json import dumps
from pathlib import Path
from secrets import randbelow, token_bytes
from subprocess import run

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from solver.crypto.ciphers import (encrypt_blob, load_private_key, lock, public_key_hex, read_enc_key_file,
                                   read_master_key, verify_master_key)
from solver.crypto.config import config
from solver.shell import console, register
from solver.utils.shell_utils import confirm

#: Reserved (non-public-key) entry in enc-key.json holding the verify-by-decrypt ciphertext.
_VERIFY: str = 'verify'


# ==================================================================================================================== #
#                                       asymmetric key: create + persist
# ==================================================================================================================== #
def _rotate_backups(key_file: Path) -> None:
    """Rotate up to `private_key_backups` rolling backups of key_file (.1 newest ... .N oldest)."""
    if not key_file.exists():
        return
    keep: int = config['private_key_backups']
    oldest: Path = key_file.with_suffix(f'.{keep}')
    if oldest.exists():
        oldest.unlink()
    for i in range(keep - 1, 0, -1):
        backup: Path = key_file.with_suffix(f'.{i}')
        if backup.exists():
            backup.rename(key_file.with_suffix(f'.{i + 1}'))
    key_file.rename(key_file.with_suffix('.1'))


def _persist_private_key(private_key: X25519PrivateKey) -> None:
    """Write the plain (unencrypted) private key to disk `0600` (rotating backups)."""
    key_file: Path = config['private_key_file']
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key_file.parent.chmod(0o700)
    _rotate_backups(key_file)
    key_file.write_bytes(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8,
                                                   NoEncryption()))
    key_file.chmod(0o600)
    load_private_key.cache_clear()
    read_master_key.cache_clear()
    console.print(f'[success]Private key written to [accent]{key_file}[/accent] '
                  f'(plain, machine-local `0600`)[/success]')


def _create_user_key() -> X25519PrivateKey:
    """Generate a fresh X25519 key pair, persist it plain (`0600`), and return the private key."""
    private_key: X25519PrivateKey = x25519.X25519PrivateKey.generate()
    _persist_private_key(private_key)
    return private_key


# ==================================================================================================================== #
#                                       master (symmetrical) key: persist + rotate
# ==================================================================================================================== #
def _write_enc_key_file(data: dict[str, str]) -> None:
    """Serialise keys/enc-key.json and clear the cached master key so the next read picks it up."""
    enc_file: Path = config['enc_key_file']
    enc_file.parent.mkdir(parents=True, exist_ok=True)
    enc_file.write_text(dumps(data, indent=2))
    read_master_key.cache_clear()
    pubkeys: int = sum(1 for k in data if k != _VERIFY)
    console.print(f'[success]Wrote [accent]{enc_file}[/accent] ({pubkeys} authorised public key(s))[/success]')


def _wrapped_for_all(master_key: bytes, public_keys: list[str]) -> dict[str, str]:
    """Build the enc-key.json body: master_key wrapped to each public key, plus the verify ciphertext."""
    data: dict[str, str] = {pub: lock(X25519PublicKey.from_public_bytes(bytes.fromhex(pub)), master_key)
                            for pub in public_keys}
    data[_VERIFY] = encrypt_blob(config['verify_text'], master_key).hex()
    return data


@register(help_text='Rotate the enc key and re-wrap to users.', aliases=('rekey',))
def key_rekey() -> int:
    """Rotate to a new master key (proof-of-possession), re-wrap to all users, and renormalise blobs.

    Because the git filter is deterministic, every committed blob depends on the master key, so a
    rotation re-encrypts the tracked private files via `git add --renormalize`.
    """
    try:
        read_master_key()  # proof of authority: must currently hold and verify the master key
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] refusing to rekey -- current key check failed ({exc})')
        return 1
    if not confirm('Rotate the master key and re-encrypt all private files?'):
        console.print('[muted]Rekey cancelled.[/muted]')
        return 1
    data: dict[str, str] = read_enc_key_file()
    new_master: bytes = token_bytes(32)
    _write_enc_key_file(_wrapped_for_all(new_master, [k for k in data if k != _VERIFY]))
    console.print('[muted]Re-encrypting tracked private files...[/muted]')
    run(['git', 'add', '--renormalize', '--', 'solutions/private'], cwd=config['root_dir'], check=False)
    console.print('[success]Master key rotated; review `git status` and commit the re-encrypted blobs.[/success]')
    return 0


@register(help_text='Authorise another public key (hex) to access the enc key.', aliases=('authorize',))
def user_authorize(public_key: str) -> int:
    """Wrap the current master key to `public_key` and add it to enc-key.json (proof-of-possession)."""
    try:
        master_key: bytes = read_master_key()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] cannot access the master key ({exc})')
        return 1
    try:
        pub: X25519PublicKey = X25519PublicKey.from_public_bytes(bytes.fromhex(public_key))
    except ValueError:
        console.print('[error]error:[/error] public_key must be 32 bytes of hex')
        return 1
    data: dict[str, str] = read_enc_key_file()
    data[public_key_hex(pub)] = lock(pub, master_key)
    _write_enc_key_file(data)
    console.print(f'[success]Public key [accent]{public_key}[/accent] authorised.[/success]')
    return 0


# ==================================================================================================================== #
#                                               user identity
# ==================================================================================================================== #
@register(help_text="Show public key & enc-key access; --regen for new key-pair.")
def user(regen: bool = False) -> int:
    """Show the current identity and whether it can decrypt; create a key pair on first run or --regen."""
    try:
        private_key: X25519PrivateKey | None = load_private_key()
    except (FileNotFoundError, ValueError):
        private_key = None
    if regen and private_key is not None and not confirm('Replace the existing private key with a new one?'):
        console.print('[muted]Keeping the existing private key.[/muted]')
        regen = False
    if regen or private_key is None:
        # Carry master-key access across the rotation: capture it with the outgoing key *before*
        # replacing it, then re-wrap it to the new key (and revoke the old entry) afterwards.
        carry: tuple[str, bytes] | None = None
        if private_key is not None:
            try:
                carry = (public_key_hex(private_key.public_key()), read_master_key())
            except (FileNotFoundError, KeyError, ValueError):
                carry = None
        private_key = _create_user_key()
        if carry is not None:
            old_pub, master_key = carry
            data: dict[str, str] = read_enc_key_file()
            data.pop(old_pub, None)  # revoke the replaced key's access
            data[public_key_hex(private_key.public_key())] = lock(private_key.public_key(), master_key)
            _write_enc_key_file(data)
    pub: str = public_key_hex(private_key.public_key())
    try:
        read_master_key()
        console.print(f'[primary]public key:[/primary] {pub}\n[success]✓ can encrypt/decrypt[/success]')
    except (FileNotFoundError, KeyError, ValueError):
        console.print(f'[primary]public key:[/primary] {pub}\n[error]✗ cannot encrypt/decrypt[/error]')
        console.print('[muted]Have an existing user `authorize` this public key, or `key-reconstruct` '
                      'from shares.[/muted]')
    return 0


# ==================================================================================================================== #
#                                       n of m secret sharing (Shamir over GF(2**521-1))
# ==================================================================================================================== #
#: 13th Mersenne prime; comfortably larger than a 256-bit secret.
_PRIME: int = 2 ** 521 - 1
#: Length of the master key in bytes, and the hex width sufficient for any value < _PRIME.
_SECRET_BYTES: int = 32
_HEX_WIDTH: int = 131


def _eval_poly(poly: list[int], x: int) -> int:
    """Evaluate `poly` at `x` (Horner's method) modulo `_PRIME`."""
    result: int = 0
    for coeff in reversed(poly):
        result = (result * x + coeff) % _PRIME
    return result


def _interpolate_at_zero(points: list[tuple[int, int]]) -> int:
    """Lagrange-interpolate the polynomial value at `x = 0` from `points` modulo `_PRIME`."""
    result: int = 0
    for i, (xi, yi) in enumerate(points):
        num: int = 1
        den: int = 1
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            num = (num * -xj) % _PRIME
            den = (den * (xi - xj)) % _PRIME
        result = (result + yi * num * pow(den, -1, _PRIME)) % _PRIME
    return result


def _split_secret(secret: bytes, num_shares: int, threshold: int) -> list[str]:
    """Split a 32-byte key into `num_shares` shares; any `threshold` reconstruct it. Each share is 262 hex chars."""
    if len(secret) != _SECRET_BYTES:
        raise ValueError(f'secret must be exactly {_SECRET_BYTES} bytes, got {len(secret)}')
    if not 1 <= threshold <= num_shares:
        raise ValueError('require 1 <= threshold <= num_shares')
    poly: list[int] = [int.from_bytes(secret, 'big')] + [randbelow(_PRIME) for _ in range(threshold - 1)]
    xs: set[int] = set()
    while len(xs) < num_shares:
        xs.add(randbelow(_PRIME - 1) + 1)
    return [f'{x:0{_HEX_WIDTH}x}{_eval_poly(poly, x):0{_HEX_WIDTH}x}' for x in xs]


def _reconstruct_secret(shares: list[str]) -> bytes:
    """Reconstruct the 32-byte key from `threshold` distinct shares produced by `_split_secret`."""
    if not shares:
        raise ValueError('need at least one share')
    points: list[tuple[int, int]] = []
    seen: set[int] = set()
    for s in shares:
        if len(s) != 2 * _HEX_WIDTH:
            raise ValueError(f'share must be {2 * _HEX_WIDTH} hex chars, got {len(s)}')
        x: int = int(s[:_HEX_WIDTH], 16)
        y: int = int(s[_HEX_WIDTH:], 16)
        if x in seen:
            raise ValueError(f'duplicate share index {x:x}')
        seen.add(x)
        points.append((x, y))
    secret_int: int = _interpolate_at_zero(points)
    if secret_int.bit_length() > _SECRET_BYTES * 8:
        raise ValueError('reconstructed value out of range; wrong threshold or corrupted shares')
    return secret_int.to_bytes(_SECRET_BYTES, 'big')


@register(help_text='Split master key into shares (n-of-m secret sharing).')
def key_split(num_shares: int = 3, threshold: int = 2) -> int:
    """Print `num_shares` Shamir shares of the current master key (threshold needed to reconstruct)."""
    if num_shares < threshold or threshold < 2:
        console.print('[error]error:[/error] threshold must be >= 2 and < num_shares')
        return 1
    try:
        master_key: bytes = read_master_key()
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f'[error]error:[/error] cannot access the master key ({exc})')
        return 1
    try:
        shares: list[str] = _split_secret(master_key, num_shares, threshold)
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    for i, share in enumerate(shares, start=1):
        console.print(f'[accent]Master key share {i} of {num_shares}:[/accent]\n[muted]{share}[/muted]\n')
    return 0


@register(help_text='Recover master key from shares.')
def key_reconstruct(threshold: int = 2) -> int:
    """Prompt for `threshold` shares, reconstruct the master key, and store it wrapped to this user."""
    try:
        private_key: X25519PrivateKey = load_private_key()
    except (FileNotFoundError, ValueError) as exc:
        console.print(f'[error]error:[/error] need a private key first ({exc}); run `user`')
        return 1
    shares: list[str] = []
    for i in range(1, threshold + 1):
        shares.append(console.input(f'[accent]Enter master key share {i} of {threshold}:[/accent] ').strip())
    try:
        master_key: bytes = _reconstruct_secret(shares)
    except ValueError as exc:
        console.print(f'[error]error:[/error] {exc}')
        return 1
    data: dict[str, str] = read_enc_key_file() if config['enc_key_file'].exists() else {}
    if _VERIFY in data and not verify_master_key(data, master_key):
        console.print('[error]error:[/error] reconstructed key fails verification; wrong shares?')
        return 1
    data[public_key_hex(private_key.public_key())] = lock(private_key.public_key(), master_key)
    data.setdefault(_VERIFY, encrypt_blob(config['verify_text'], master_key).hex())
    _write_enc_key_file(data)
    console.print(f'[success]Master key reconstructed from {threshold} shares and stored.[/success]')
    return 0
