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

import os
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
    # per-user vault (envelope encryption of the private key + env)
    env_file: Path  # the project env file (ANTHROPIC_API_KEY etc.) -- the vault's second secret
    vault_file: Path  # {salt, iterations, wrapped_vk}: the vault key wrapped under the password key
    user_pass_file: Path  # terminal-only: the password, to derive the password key off-line
    vault_magic: bytes  # header marking a file as vault-encrypted (vs. plaintext at rest)
    vault_kdf_iterations: int  # PBKDF2-HMAC-SHA256 rounds deriving the password key from the password
    vault_key_env: str  # env var naming the uid-private tmpfs file that holds the session vault key
    # git-filter wire format
    magic: bytes
    nonce_len: int
    header_len: int
    filter_name: str
    attr_line: str
    pkt_max: int  # max pkt-line payload (65520 - 4-byte length prefix)
    verify_text: bytes  # fixed known plaintext for the verify-by-decrypt master-key check


def _root_dir() -> Path:
    """Return the repository root (pure: captures git's output, no chdir / PATH side-effects).

    ``EULER_REPO_ROOT`` wins when set — the deployed web tier points every service
    at the real working tree with it (``solver.config`` honours the same var), and
    the git filter must agree with the shell on where the tree is. Otherwise ask git
    (authoritative for a checkout), and finally fall back to this file's own location
    (``solver/crypto/config.py`` → up 2). The fallbacks matter: the **web shells run
    as ``euler-ws-*`` uids that do not own the checkout**, so git refuses
    with *detected dubious ownership*, and git may not be installed at all in a deployed
    tier that does no git operations by design. This module is imported at shell startup
    (the crypto commands register from it), so a hard failure here would take the whole
    shell down over a path this package can derive itself.
    """
    override = os.environ.get('EULER_REPO_ROOT', '').strip()
    if override and (root_override := Path(override)).is_dir():
        return root_override
    # Shed git's own environment before probing: when git runs the filter (stash,
    # rebase, checkout) it exports GIT_DIR — and with GIT_DIR set but no
    # GIT_WORK_TREE, `rev-parse --show-toplevel` reports the CWD as the toplevel,
    # deriving a root of solver/crypto and a secrets dir of solver/.crypto — the
    # filter then can't find the key and dies mid-protocol. The probe must resolve
    # from its own cwd path alone.
    probe_env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    try:
        result = run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True,
                     cwd=Path(__file__).parent, env=probe_env)
    except OSError:                                   # git not installed at all
        result = None
    if result is not None and result.returncode == 0 and (root := result.stdout.strip()):
        return Path(root)
    fallback = Path(__file__).resolve().parents[2]
    if not (fallback / 'solver').is_dir():
        raise ValueError('solver.crypto: failed to locate the repository root')
    return fallback


_ROOT: Path = _root_dir()
#: Machine-local secrets dir: a sibling dot-directory named for the repo (e.g.
#: repo `~/euler` -> `~/.euler`), *outside* the checkout so secrets never sit in
#: the work tree. Holds the plain private key and the project env file; only
#: `enc-key.json` (wrapped master keys, useless without a private key) stays in-repo.
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
    'enc_key_file': _ROOT / 'keys' / 'enc-key.json',  # {<public-key-hex>: <locked-master-key-hex>} + 'verify'
    'private_key_backups': 5,  # rolling backups kept of the private key file
    # per-user vault: both `id` and `env` live encrypted under a random vault key, itself
    # wrapped under a password-derived key; the plaintext key only ever exists in a tmpfs file.
    'env_file': _SECRETS_DIR / 'env',  # same value as solver.config.env_file, kept import-free here
    'vault_file': _SECRETS_DIR / 'vault',  # {salt, iterations, wrapped_vk}
    'user_pass_file': _SECRETS_DIR / 'user_pass',  # terminal-only password, to derive the key off-line
    'vault_magic': _VAULT_MAGIC,
    'vault_kdf_iterations': 600_000,  # PBKDF2-HMAC-SHA256; WebCrypto-native so a browser can derive the same key
    'vault_key_env': 'EULER_VAULT_KEY_FILE',
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
