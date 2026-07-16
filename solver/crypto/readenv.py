#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Print the authoring env (``~/.euler/env``) as plaintext — the setup scripts' reader.

``~/.euler/env`` is the **authoring source** for deployment config: the FQDN, the DNS-01
credentials, the SMTP relay's login. The installers (``scripts/setup/*.sh``) used to
``.``-source it, which stops working the moment the vault encrypts it — so they source
this instead (``scripts/setup/authoring_env.sh``), and it hands back the same dotenv lines
whether the file rests as plaintext or as ciphertext.

**This module is a CLI, not a library, and it prints secrets on stdout by design.** It
therefore prints only under ``__main__`` — importing it emits nothing — and, critically,
**nothing on the git-filter path may ever import it**: :mod:`solver.crypto.vault` and
:mod:`solver.crypto.ciphers` run there, where stdout belongs to git and a stray byte
corrupts a blob. The dependency only ever points this way (here → ``vault``), never back.

**The password**, in the order the operator asked for:

1. an already-unlocked session (``$EULER_VAULT_KEY_FILE``) — a shell that has unlocked
   passes it to its children for free;
2. ``$EULER_VAULT_PASSWORD`` — a script, CI, an unattended run;
3. the operator, prompted on **/dev/tty** (not stdin: stdin is usually the calling
   script's, and reading it would eat the installer's own input).

Deliberately stdlib + ``cryptography`` only, through :mod:`solver.crypto.vault`'s
non-interactive surface: it runs during installs, sometimes under ``sudo``, sometimes
before much else exists. It reads the *repo-derived* secrets dir (``~euler`` →
``~/.euler``, see :mod:`solver.crypto.config`), never ``$HOME``, so running it as root
still reads the operator's vault rather than root's.
"""
from __future__ import annotations

__all__ = ['main']

import getpass
import sys
from pathlib import Path

from cryptography.exceptions import InvalidTag

from solver.crypto import vault
from solver.crypto.config import config


def _resolve_vault_key() -> bytes | None:
    """The vault key: the session's, else the env password, else ask the operator."""
    if (vault_key := vault.session_vault_key()) is not None:
        return vault_key
    try:
        password: str = getpass.getpass('Vault password: ', stream=sys.stderr)
    except (EOFError, OSError):
        # No tty (a service, a pipe): there is no one to ask.
        print('error: the vault is locked and there is no terminal to ask; '
              f'set ${config["vault_password_env"]}', file=sys.stderr)
        return None
    if not password:
        return None
    try:
        return vault.unlock_vault(password)
    except InvalidTag:
        print('error: wrong vault password', file=sys.stderr)
        return None


def main(argv: list[str] | None = None) -> int:
    """Print an env file's plaintext on stdout. 0 on success, 1 on any failure.

    Usage: ``python -m solver.crypto.readenv [PATH]`` — *PATH* defaults to the authoring
    env (``~/.euler/env``). It is an argument rather than always the default because the
    caller (``scripts/setup/authoring_env.sh``) names the file it wants: a reader that
    quietly substituted a different file than the one it was handed would be right only
    by coincidence.
    """
    args: list[str] = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print('usage: python -m solver.crypto.readenv [PATH]', file=sys.stderr)
        return 1
    env_file: Path = Path(args[0]) if args else config['env_file']
    if not env_file.exists():
        print(f'error: no authoring env at {env_file}', file=sys.stderr)
        return 1
    raw: bytes = env_file.read_bytes()
    # A plaintext env is not an error: it is the state before `vault init`, and the
    # installers must keep working across that migration in both directions.
    if not vault.is_vault_encrypted(raw):
        sys.stdout.write(raw.decode('utf-8'))
        return 0
    if not vault.vault_exists():
        print(f'error: {env_file} is vault-encrypted but {config["vault_file"]} is missing — '
              'its key is unrecoverable without it; restore that file from backup',
              file=sys.stderr)
        return 1
    vault_key: bytes | None = _resolve_vault_key()
    if vault_key is None:
        return 1
    try:
        sys.stdout.write(vault.decrypt_secret(vault_key, raw).decode('utf-8'))
    except InvalidTag:
        print(f'error: this key does not decrypt {env_file} (a foreign vault?)', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
