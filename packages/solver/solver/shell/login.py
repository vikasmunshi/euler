#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Login: who the session runs as, and whether its vault is open — settled before any command.

docs/package-guide.md § 2. Two steps, both run by :func:`solver.main.main`:

1. :func:`identify` — the :class:`~solver.auth.Subject`, before any command module loads,
   because each command's floor is checked against it as it registers. The solver shell's
   own identity is the OS login with a role from the root-owned policy
   (:mod:`solver.auth.identity`); an :class:`~solver.shell.extension.Extension` may supply
   another (the web shell redeems a one-time ticket).
2. :func:`unlock` — the vault gate. `id` and `env` rest encrypted, and the readers that need
   them — the git clean/smudge filter above all — are subprocesses with no terminal to be
   asked anything: the key must reach them as the inherited key file this materialises. So
   the asking happens here, once, at the one moment there is still a person to ask. It is a
   no-op when there is no vault and when `$EULER_VAULT_KEY_FILE` / `$EULER_VAULT_PASSWORD`
   answer. A declined or wrong password is not fatal — the shell runs locked, and the private
   solutions and `claude-api` are what stay unavailable. The vault is a capability, not an
   identity proof (§ 2.2): the uid already said who this is.
"""
from __future__ import annotations

__all__ = ['identify', 'unlock']

from solver.auth import Subject
from solver.config import config
from solver.crypto.keys import unlock_session
from solver.shell.extension import Extension


def identify(extension: Extension | None = None) -> Subject:
    """Settle `config.subject`: the extension's identity if it brings one, else the OS login's."""
    if extension is not None and extension.identity is not None:
        config.subject = extension.identity()
    return config.subject


def unlock(extension: Extension | None = None) -> None:
    """Open the vault for this session and its children — prompting only if the front end allows."""
    unlock_session(interactive=extension is None or extension.prompt_vault)
