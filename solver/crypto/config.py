#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Crypto configuration: the single source of truth for every file location and git-filter wire constant.

The crypto package does **not** import `solver.config` -- the repo root comes from
`solver.utils.repo_root` (stdlib-only, one implementation for the whole solver) and everything
else hangs off it. `config` is a `CryptoConfig` TypedDict, so every
`config['...']` access elsewhere in `solver.crypto` is type-checked against the field's declared type.

This module is imported (transitively) on the git-filter path, where stdout carries file content, so
it must emit **nothing on stdout** at import time; it depends only on the standard library.
"""
from __future__ import annotations

__all__ = ['config']

from pathlib import Path
from typing import TypedDict

from solver.utils.repo_root import repo_root


# ==================================================================================================================== #
#                                               configuration
# ==================================================================================================================== #
class CryptoConfig(TypedDict):
    """All crypto configuration: file locations and git-filter wire-format constants."""

    root_dir: Path
    # key material
    private_key_file: Path  # plain (unencrypted) X25519 private key (PKCS8 PEM)
    enc_key_file: Path  # THIS machine's two records: {verify, <my-public-key-hex>: <wrapped master key>}
    enc_key_verify: str  # the reserved entry name: the verify-by-decrypt ciphertext
    private_key_backups: int  # rolling backups kept of the private key file
    # per-user vault (envelope encryption of the private key + env)
    env_file: Path  # the project env file (ANTHROPIC_API_KEY etc.) -- the vault's second secret
    vault_file: Path  # {salt, iterations, wrapped_vk}: the vault key wrapped under the password key
    vault_magic: bytes  # header marking a file as vault-encrypted (vs. plaintext at rest)
    vault_kdf_iterations: int  # PBKDF2-HMAC-SHA256 rounds deriving the password key from the password
    vault_key_env: str  # env var naming the uid-private tmpfs file that holds the session vault key
    vault_password_env: str  # env var carrying the vault password itself (non-interactive unlock)
    # git-filter wire format
    magic: bytes
    nonce_len: int
    header_len: int
    filter_name: str
    attr_path: str
    attr_line: str
    pkt_max: int  # max pkt-line payload (65520 - 4-byte length prefix)
    verify_text: bytes  # fixed known plaintext for the verify-by-decrypt master-key check


_ROOT: Path = repo_root()
#: Machine-local secrets dir: a sibling dot-directory named for the repo (e.g.
#: repo `~/euler` -> `~/.euler`), *outside* the checkout so secrets never sit in
#: the work tree. Holds the plain private key and the project env file; only
#: Holds the private key, the project env file, and the wrapped master key -- nothing about
#: key material lives in the checkout any more.
_SECRETS_DIR: Path = _ROOT.parent / f'.{_ROOT.name}'
_MAGIC: bytes = b'SLVR\x01'  # 4-byte tag + 1-byte format version
_NONCE_LEN: int = 12
_FILTER_NAME: str = 'solver-crypt'  # git filter driver name (.gitattributes / git config)
_VAULT_MAGIC: bytes = b'VLT\x01'  # 3-byte tag + 1-byte format version; marks a vault-encrypted secret

#: All crypto configuration -- file locations and git-filter wire-format constants -- in one place.
config: CryptoConfig = {
    'root_dir': _ROOT,
    # key material
    'private_key_file': _SECRETS_DIR / 'id',  # plain (unencrypted) X25519 private key (PKCS8 PEM)
    # The master key, wrapped to THIS machine's public key. Two records and nothing else:
    # `verify`, and the holder's own entry. It lives in the machine-local secrets dir beside
    # the private key that opens it — NOT in the checkout.
    #
    # It used to be a tracked, multi-entry file: every authorised key, committed, distributed
    # by git. That put per-machine key material into shared state, and everything that hurt
    # followed from it — a rotation dirtied a tracked file, `sync.sh` stashed and popped it
    # around the merge, the pop conflicted with the authorised copy coming the other way, and
    # the conflict markers left the JSON unparseable, which every reader takes for "not
    # authorised". A reader could not even recover: `git-reset` is contributor-floored. It
    # also needed an attribution map and a purge verb to answer "whose entries are these",
    # a machine-local overlay to bridge rotations, and a repair path in `git-sync`.
    #
    # One file per machine needs none of that. Distribution is the message spool (a
    # maintainer's `user-authorize` replies with the payload, `msg save` writes it), and a
    # rotation just re-wraps in place.
    'enc_key_file': _SECRETS_DIR / 'enc-key.json',
    'enc_key_verify': 'verify',
    'private_key_backups': 5,  # rolling backups kept of the private key file
    # per-user vault: both `id` and `env` live encrypted under a random vault key, itself
    # wrapped under a password-derived key; the plaintext key only ever exists in a tmpfs file.
    'env_file': _SECRETS_DIR / 'env',  # same value as solver.config.env_file, kept import-free here
    'vault_file': _SECRETS_DIR / 'vault',  # {salt, iterations, wrapped_vk}
    'vault_magic': _VAULT_MAGIC,
    'vault_kdf_iterations': 600_000,  # PBKDF2-HMAC-SHA256; WebCrypto-native so a browser can derive the same key
    'vault_key_env': 'EULER_VAULT_KEY_FILE',
    # The password itself, for a non-interactive unlock (CI, a setup script, an automated
    # run). Deliberately an env var and NOT a file in the secrets dir: a password stored
    # beside the ciphertext it unlocks is not a second factor, it is a decoration.
    'vault_password_env': 'EULER_VAULT_PASSWORD',
    # git-filter wire format
    'magic': _MAGIC,
    'nonce_len': _NONCE_LEN,
    'header_len': len(_MAGIC) + _NONCE_LEN,
    'filter_name': _FILTER_NAME,
    # Must stay identical to the rule in the **tracked** `.gitattributes`: the installer
    # matches on it, and a drift makes it append a second, weaker copy of the rule to a
    # tracked file — a dirty working tree in every collaborator clone. The path prefix is
    # split out so the matcher can recognise the rule without pinning its flags.
    'attr_path': 'solutions/private/**',
    'attr_line': f'solutions/private/** filter={_FILTER_NAME} -text -diff',
    'pkt_max': 65516,  # max pkt-line payload (65520 - 4-byte length prefix)
    # Fixed known plaintext for the verify-by-decrypt master-key check: the opening quatrain of
    # "Auguries of Innocence" by William Blake.
    'verify_text': (
        b'To see a World in a Grain of Sand\n'
        b'And a Heaven in a Wild Flower\n'
        b'Hold Infinity in the palm of your hand\n'
        b'And Eternity in an hour\n'
    ),
}
