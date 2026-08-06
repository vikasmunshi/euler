#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Crypto configuration: the single source of truth for every file location and git-filter wire constant.

The crypto package takes **only the anchors** from `solver.config.paths` -- `repo_root()` and
`secrets_dir()`, stdlib-only and side-effect-free, one implementation for the whole solver --
and hangs everything else off them. It never touches the `Config` singleton's dynamic half:
resolving an identity, or moving the process, on the git-filter path is exactly the kind of
thing that ends with a filter confidently reading the wrong tree. `config` is a
`CryptoConfig` TypedDict, so every
`config['...']` access elsewhere in `solver.crypto` is type-checked against the field's declared type.

This module is imported (transitively) on the git-filter path, where stdout carries file content, so
it must emit **nothing on stdout** at import time; it depends only on the standard library.
"""
from __future__ import annotations

__all__ = ['SHARE_FILE_ENV', 'config']

import os
from pathlib import Path
from typing import TypedDict

from solver.config.paths import repo_root, secrets_dir


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
    share_file: Path  # this machine's half of the master key (`key-split`) -- operational, never tracked
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


#: Environment override for the share file (tests, and a machine that keeps it elsewhere).
SHARE_FILE_ENV: str = 'EULER_SHARE_FILE'
#: The deployed location: beside `authorizations.json`, root-owned and world-readable ON THE
#: HOST. Readable is the point -- `key-split` and `key-reconstruct` only ever read it, so a
#: maintainer's web shell (which can never obtain sudo) keeps working; only the operator writes.
_SYSTEM_SHARE: Path = Path('/etc/euler/share.json')


def _resolve_share_file(secrets_dir: Path) -> Path:
    """Where this machine's half of the master key lives.

    Three candidates, in order, and the reason for each:

    1. **`$EULER_SHARE_FILE`** -- the tests, and any machine that keeps it elsewhere.
    2. **`/etc/euler/share.json`**, when that directory exists: a deployed host. It is
       operational state, not repository content -- committing it would publish the half to
       everyone with a clone, and this repository is public, which would make "and a current
       clone" no barrier at all to anybody.
    3. **`~/.euler/share.json`** otherwise -- a plain checkout with no deployed tier, where
       the secrets dir is already the machine-local home for key material.

    The *directory* is probed rather than the file, so the first `key-split` on a deployed
    host writes to the deployed location rather than inventing a second one in `~`.
    """
    override: str = os.environ.get(SHARE_FILE_ENV, '').strip()
    if override:
        return Path(override)
    return _SYSTEM_SHARE if _SYSTEM_SHARE.parent.is_dir() else secrets_dir / 'share.json'


_ROOT: Path = repo_root()
#: Machine-local secrets dir: a sibling dot-directory named for the repo (e.g.
#: repo `~/euler` -> `~/.euler`), *outside* the checkout so secrets never sit in
#: the work tree. Holds the private key, the project env file, and the wrapped master
#: key -- nothing about key material lives in the checkout any more.
_SECRETS_DIR: Path = secrets_dir(_ROOT)
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
    # maintainer's `user-authorize` replies with the payload, `msg act` writes it), and a
    # rotation just re-wraps in place.
    'enc_key_file': _SECRETS_DIR / 'enc-key.json',
    'enc_key_verify': 'verify',
    'private_key_backups': 5,  # rolling backups kept of the private key file
    # One half of a 2-of-2 split of the master key (`key-split`), plus the `verify` record
    # saying which key it belongs to. **Operational state, never tracked.** A single share is
    # a uniformly random point — independent of the secret — so committing it would leak
    # nothing mathematically, and it was tracked for exactly that reason. It moved here
    # because the repository is *public*: a half everyone can clone is not a second factor,
    # so the sealed message plus the recipient's private key was the whole of it. Kept on the
    # host, the two halves are protected by different things again.
    'share_file': _resolve_share_file(_SECRETS_DIR),
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
