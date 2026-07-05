#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `users` shell command: manage web-auth accounts from the solver shell.

Registration is invite-only. ``users add <email>`` creates a **disabled,
password-less** account in ``keys/.users.json`` and emails a **secure link** (valid
24 h); the user opens it and chooses their own password in the browser at
``/register`` (the server never sees it). If Gmail SMTP is not configured, the link
is printed on the console so the admin can deliver it manually. The other actions
manage existing accounts.
"""
from __future__ import annotations

__all__ = ['users']

from typing import Literal

from solver.config import ExitCodes, config
from solver.shell import console, register
from solver.web.auth import mail
from solver.web.auth.pending import PendingStore
from solver.web.auth.users import UserStore, normalize_email


@register(help_text='Manage web-auth users ([accent.dim]list|add|reset|remove|disable|enable[/accent.dim]).')
def users(action: Literal['list', 'add', 'reset', 'remove', 'disable', 'enable'] = 'list',
          email: str = '') -> int:
    """List or manage the web-auth accounts in `keys/.users.json`.

    Args:
        action:  'list' (default) shows every account; 'add' invites an email
                 (disabled + emailed secure link; the user sets their own password
                 at /register); 'reset' emails a fresh link so a registered user can
                 choose a new password; 'remove' deletes an account; 'disable' /
                 'enable' toggle whether a registered account may log in.
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
        return _invite_user(store, PendingStore(config.pending_file), key)
    if action == 'reset':
        return _reset_user(store, PendingStore(config.pending_file), key)
    if action == 'remove':
        removed = store.remove(key)
        PendingStore(config.pending_file).remove_email(key)  # also drop any pending link
        return _report(removed, f'removed {key}', f'no such user: {key}')
    if action == 'disable':
        return _report(store.set_disabled(key, True), f'disabled {key}', f'no such user: {key}')
    return _report(store.set_disabled(key, False), f'enabled {key}', f'no such user: {key}')


def _list_users(store: UserStore) -> int:
    """Print every account with its status (invited / active / disabled) and created date."""
    records = store.records()
    if not records:
        console.print('[muted]no web-auth users (invite one with: users add <email>)[/muted]')
        return ExitCodes.EXIT_OK
    width = max(len(r.email) for r in records) + 1
    for record in records:
        if not record.registered:
            status = '[warning]invited[/warning]'
        elif record.disabled:
            status = '[error]disabled[/error]'
        else:
            status = '[success]active[/success]'
        console.print(f'[accent.dim]{record.email:<{width}}[/accent.dim] {status} [muted]{record.created}[/muted]')
    return ExitCodes.EXIT_OK


def _invite_user(store: UserStore, pending: PendingStore, key: str) -> int:
    """Invite `key`: create a disabled account, mint a secure link, and email it."""
    record = store.get(key)
    if record is not None and record.registered:
        console.print(f'[error]error:[/error] [muted]{key} is already registered '
                      f'(use `users reset` to send a new-password link, or remove it first)[/muted]')
        return ExitCodes.EXIT_ERROR
    store.invite(key)
    token = pending.invite(key, 'register')
    return _deliver_link(key, token, 'register', f'[success]invited {key}[/success] '
                         f'[muted]— link emailed; they set their password at /register[/muted]')


def _reset_user(store: UserStore, pending: PendingStore, key: str) -> int:
    """Send a fresh secure link so a registered `key` can choose a new password at /register.

    The account stays enabled and keeps its current password until the user completes
    the reset (registration overwrites the verifier), so a reset never locks anyone out.
    """
    record = store.get(key)
    if record is None or not record.registered:
        console.print(f'[error]error:[/error] [muted]{key} is not a registered user[/muted]')
        return ExitCodes.EXIT_ERROR
    token = pending.invite(key, 'reset')
    return _deliver_link(key, token, 'reset', f'[success]reset link sent to {key}[/success] '
                         f'[muted]— they set a new password at /register[/muted]')


def _deliver_link(key: str, token: str, kind: str, success: str) -> int:
    """Email the secure `kind` link to `key`; on SMTP failure print it for manual delivery."""
    try:
        mail.send_registration_link(key, token, kind)
    except Exception as exc:
        console.print(f'[warning]could not email link to {key}:[/warning] [muted]{exc}[/muted]')
        console.print(f'[muted]deliver this link to {key} manually (valid 24 h):[/muted] '
                      f'[accent]{mail.registration_link(token)}[/accent]')
        return ExitCodes.EXIT_OK
    console.print(success)
    return ExitCodes.EXIT_OK


def _report(ok: bool, success: str, failure: str) -> int:
    """Print `success`/`failure` for a boolean store operation and map it to an exit code."""
    if ok:
        console.print(f'[success]{success}[/success]')
        return ExitCodes.EXIT_OK
    console.print(f'[error]error:[/error] [muted]{failure}[/muted]')
    return ExitCodes.EXIT_ERROR
