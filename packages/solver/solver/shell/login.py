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

What the two steps settled, :func:`status_line` reports — the start-up banner's line.
"""
from __future__ import annotations

__all__ = ['identify', 'status_line', 'unlock']

from rich.markup import escape

from solver.auth import Subject
from solver.config import config
from solver.crypto import vault
from solver.crypto.ciphers import read_master_key
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


def status_line() -> tuple[str, ...]:
    """The banner's status line, as markup segments: who, what it can decrypt, what it runs.

    `<user> · <profile> · <channel>`, then the vault and master-key state, then the clone's
    `git describe` — the build number is the banner's own first line. Segments, so a
    narrow terminal wraps between them rather than inside one. Read-only and quiet: every
    probe degrades to a word rather than raising, never prompts and never writes — a broken
    key file must not stop the shell starting, and this is not the place to mend one (that
    is `user` / `vault`).
    """
    # Imported here: the module registers the `version` command, and login loads before them.
    from solver.utils.version import git_describe

    subject = config.subject
    segments: list[str] = [f'[primary]{escape(subject.user)}[/primary] · {subject.profile} · {subject.channel}',
                           f'{_vault_state()} · {_master_key_state()}']
    if detail := git_describe(timeout=1):
        segments.append(f'git {detail}')
    return tuple(segments)


def _vault_state() -> str:
    """The vault, in a word or two: absent, locked or unlocked for this session."""
    if not vault.vault_exists():
        return '[warning]no vault[/warning]'
    if vault.session_vault_key() is None:
        return '[error]vault locked[/error]'
    return '[success]vault unlocked[/success]'


def _master_key_state() -> str:
    """Whether this session holds the master key — and, if not, which step is missing."""
    if vault.vault_exists() and vault.session_vault_key() is None:
        return 'master key [muted]locked[/muted]'  # the id cannot be read; nothing to probe
    try:
        read_master_key()
    except FileNotFoundError:
        missing = 'no identity' if not config.private_key_file.exists() else 'not issued'
        return f'master key [warning]{missing}[/warning]'
    except KeyError:
        return 'master key [warning]not authorized[/warning]'
    except Exception:  # noqa: BLE001 — a malformed key file is reported, never raised at start-up
        return 'master key [error]invalid[/error]'
    return 'master key [success]✓[/success]'
