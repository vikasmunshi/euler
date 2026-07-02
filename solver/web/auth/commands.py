#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `users` shell command: manage web-auth accounts from the solver shell.

Bootstraps and administers the SRP verifier store at ``keys/users.json``. The
``add`` action prompts for a password locally and stores only the derived
verifier — used to create the first account before the emailed-OTP invite flow
exists (milestone 3). SRP binds the password to the **normalised** email, so the
browser login must use the same normalisation (trim + lower-case), which
``solver.web.auth.users.normalize_email`` and the JS client both apply.
"""
from __future__ import annotations

__all__ = ['users']

from typing import Literal

from solver.config import ExitCodes, config
from solver.shell import console, register
from solver.web.auth import policy
from solver.web.auth.srp import SrpToken
from solver.web.auth.users import UserStore, normalize_email


@register(help_text='Manage web-auth users ([accent.dim]list|add|remove|disable|enable[/accent.dim]).')
def users(action: Literal['list', 'add', 'remove', 'disable', 'enable'] = 'list', email: str = '') -> int:
    """List or manage the web-auth accounts in `keys/users.json`.

    Args:
        action:  'list' (default) shows every account; 'add' creates or resets an
                 account's password (prompts locally); 'remove' deletes one;
                 'disable' / 'enable' toggle whether the account may log in.
        email:   The account email (required for every action except 'list').
    """
    store = UserStore(config.users_file)
    if action == 'list':
        return _list_users(store)

    key = normalize_email(email)
    if not key:
        console.print('[error]error:[/error] [muted]an email is required for this action[/muted]')
        return ExitCodes.EXIT_ERROR

    if action == 'add':
        return _add_user(store, key)
    if action == 'remove':
        return _report(store.remove(key), f'removed {key}', f'no such user: {key}')
    if action == 'disable':
        return _report(store.set_disabled(key, True), f'disabled {key}', f'no such user: {key}')
    return _report(store.set_disabled(key, False), f'enabled {key}', f'no such user: {key}')


def _list_users(store: UserStore) -> int:
    """Print every account with its created date and status."""
    records = store.records()
    if not records:
        console.print('[muted]no web-auth users (add one with: users add <email>)[/muted]')
        return ExitCodes.EXIT_OK
    width = max(len(r.email) for r in records) + 1
    for record in records:
        status = '[error]disabled[/error]' if record.disabled else '[success]active[/success]'
        console.print(f'[accent.dim]{record.email:<{width}}[/accent.dim] {status} [muted]{record.created}[/muted]')
    return ExitCodes.EXIT_OK


def _add_user(store: UserStore, key: str) -> int:
    """Prompt for a password, then create or reset the account's SRP verifier."""
    password = console.input('[accent]Choose a password:[/accent] ', password=True)
    if len(password) < policy.MIN_PASSWORD_LENGTH:
        console.print(f'[error]error:[/error] [muted]password must be at least '
                      f'{policy.MIN_PASSWORD_LENGTH} characters[/muted]')
        return ExitCodes.EXIT_ERROR
    if password != console.input('[accent]Confirm password:[/accent] ', password=True):
        console.print('[error]error:[/error] [muted]passwords do not match[/muted]')
        return ExitCodes.EXIT_ERROR
    existed = store.get(key) is not None
    store.put(key, SrpToken.create(key, password))
    console.print(f'[success]{"updated" if existed else "added"} {key}[/success]')
    return ExitCodes.EXIT_OK


def _report(ok: bool, success: str, failure: str) -> int:
    """Print `success`/`failure` for a boolean store operation and map it to an exit code."""
    if ok:
        console.print(f'[success]{success}[/success]')
        return ExitCodes.EXIT_OK
    console.print(f'[error]error:[/error] [muted]{failure}[/muted]')
    return ExitCodes.EXIT_ERROR
