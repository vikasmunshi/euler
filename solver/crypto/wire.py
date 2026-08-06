#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The crypto wire formats: what two clones must agree on, byte for byte.

Not configuration. Every constant here is part of a format that something else already
depends on — a blob in git, a JSON file on another machine, a key the browser derives, a
rule in the tracked `.gitattributes`. Changing one does not adjust behaviour, it makes
existing data unreadable, so none of it belongs in `values.conf` and none of it has an
override. Where the *files* are is the configurable part, and that lives with every other
setting in :mod:`solver.config`.

They were one table until the split, which read naturally enough until you needed to answer
"may I change this?" — and the table had no opinion.

Import the module, not the names (`from solver.crypto import wire`, then
`wire.VAULT_KDF_ITERATIONS`): the tests lower the KDF cost to keep the vault suite fast,
and a from-import would bind the expensive value past their reach.

Stdlib-only and silent on stdout at import: this is on the git-filter path, where stdout
carries file content.
"""
from __future__ import annotations

__all__ = ['ATTR_LINE', 'ATTR_PATH', 'ENC_KEY_VERIFY', 'FILTER_NAME', 'HEADER_LEN', 'MAGIC',
           'NONCE_LEN', 'PKT_MAX', 'VAULT_KDF_ITERATIONS', 'VAULT_KEY_ENV', 'VAULT_MAGIC',
           'VAULT_PASSWORD_ENV', 'VERIFY_TEXT']

# -- the git clean/smudge blob format ---------------------------------------------------

#: 4-byte tag + 1-byte format version, at the head of every encrypted blob.
MAGIC: bytes = b'SLVR\x01'
#: AES-GCM nonce, following the magic.
NONCE_LEN: int = 12
#: What to skip to reach the ciphertext.
HEADER_LEN: int = len(MAGIC) + NONCE_LEN

#: The git filter driver's name, in `.gitattributes` and in `git config`.
FILTER_NAME: str = 'solver-crypt'
#: The path prefix the rule covers, split out so the matcher can recognise the rule
#: without pinning its flags.
ATTR_PATH: str = 'solutions/private/**'
#: Must stay identical to the rule in the **tracked** `.gitattributes`: the installer
#: matches on it, and a drift makes it append a second, weaker copy of the rule to a
#: tracked file — a dirty working tree in every collaborator clone.
ATTR_LINE: str = f'{ATTR_PATH} filter={FILTER_NAME} -text -diff'
#: Max pkt-line payload on the filter protocol (65520 − the 4-byte length prefix).
PKT_MAX: int = 65516

# -- the master-key check ---------------------------------------------------------------

#: The reserved entry name in `enc-key.json`: the verify-by-decrypt ciphertext.
ENC_KEY_VERIFY: str = 'verify'
#: Fixed known plaintext for that check: the opening quatrain of "Auguries of Innocence"
#: by William Blake.
VERIFY_TEXT: bytes = (
    b'To see a World in a Grain of Sand\n'
    b'And a Heaven in a Wild Flower\n'
    b'Hold Infinity in the palm of your hand\n'
    b'And Eternity in an hour\n'
)

# -- the per-user vault -----------------------------------------------------------------

#: 3-byte tag + 1-byte format version; marks a secret as vault-encrypted rather than
#: plaintext at rest.
VAULT_MAGIC: bytes = b'VLT\x01'
#: PBKDF2-HMAC-SHA256 rounds deriving the password key. WebCrypto-native, and matched by
#: the browser deriving the same key — which is why it is protocol and not a knob.
VAULT_KDF_ITERATIONS: int = 600_000
#: Env var naming the uid-private tmpfs file that holds the session vault key.
VAULT_KEY_ENV: str = 'EULER_VAULT_KEY_FILE'
#: Env var carrying the vault password itself, for a non-interactive unlock (CI, a setup
#: script, an automated run). Deliberately an env var and NOT a file in the secrets dir: a
#: password stored beside the ciphertext it unlocks is not a second factor, it is a
#: decoration.
VAULT_PASSWORD_ENV: str = 'EULER_VAULT_PASSWORD'
