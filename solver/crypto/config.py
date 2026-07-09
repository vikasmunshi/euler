#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Crypto configuration: the single source of truth for every file location and git-filter wire constant.

The crypto package does **not** import `solver.config` -- the repo root is discovered here with
`git rev-parse` and everything else hangs off it. `config` is a `CryptoConfig` TypedDict, so every
`config['...']` access elsewhere in `solver.crypto` is type-checked against the field's declared type.

This module is imported (transitively) on the git-filter path, where stdout carries file content, so
it must emit **nothing on stdout** at import time; it depends only on the standard library.
"""
from __future__ import annotations

__all__ = ['config']

from pathlib import Path
from subprocess import run
from typing import TypedDict


# ==================================================================================================================== #
#                                               configuration
# ==================================================================================================================== #
class CryptoConfig(TypedDict):
    """All crypto configuration: file locations and git-filter wire-format constants."""

    root_dir: Path
    # key material
    private_key_file: Path  # plain (unencrypted) X25519 private key (PKCS8 PEM)
    enc_key_file: Path  # {<public-key-hex>: <locked-master-key-hex>} + 'verify'
    private_key_backups: int  # rolling backups kept of the private key file
    # git-filter wire format
    magic: bytes
    nonce_len: int
    header_len: int
    filter_name: str
    attr_line: str
    pkt_max: int  # max pkt-line payload (65520 - 4-byte length prefix)
    verify_text: bytes  # fixed known plaintext for the verify-by-decrypt master-key check


def _root_dir() -> Path:
    """Return the git repository root (pure: captures git's output, no chdir / PATH side-effects)."""
    result = run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, cwd=Path(__file__).parent)
    if result.returncode != 0 or not (root := result.stdout.strip()):
        raise ValueError('solver.crypto: failed to locate the git repository root')
    return Path(root)


_ROOT: Path = _root_dir()
#: Machine-local secrets dir: a sibling dot-directory named for the repo (e.g.
#: repo `~/euler` -> `~/.euler`), *outside* the checkout so secrets never sit in
#: the work tree. Holds the plain private key and the project env file; only
#: `enc-key.json` (wrapped master keys, useless without a private key) stays in-repo.
_SECRETS_DIR: Path = _ROOT.parent / f'.{_ROOT.name}'
_MAGIC: bytes = b'SLVR\x01'  # 4-byte tag + 1-byte format version
_NONCE_LEN: int = 12
_FILTER_NAME: str = 'solver-crypt'  # git filter driver name (.gitattributes / git config)

#: All crypto configuration -- file locations and git-filter wire-format constants -- in one place.
config: CryptoConfig = {
    'root_dir': _ROOT,
    # key material
    'private_key_file': _SECRETS_DIR / 'id',  # plain (unencrypted) X25519 private key (PKCS8 PEM)
    'enc_key_file': _ROOT / 'keys' / 'enc-key.json',  # {<public-key-hex>: <locked-master-key-hex>} + 'verify'
    'private_key_backups': 5,  # rolling backups kept of the private key file
    # git-filter wire format
    'magic': _MAGIC,
    'nonce_len': _NONCE_LEN,
    'header_len': len(_MAGIC) + _NONCE_LEN,
    'filter_name': _FILTER_NAME,
    'attr_line': f'solutions/private/** filter={_FILTER_NAME} -text',
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
