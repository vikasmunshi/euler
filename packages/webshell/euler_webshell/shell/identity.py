#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web shell's identity: a one-time shell ticket, redeemed at the auth service.

The per-user service mints a ticket against the browser's live session and forks
`python -m euler_webshell.shell` with it in `SOLVER_TICKET` (docs/web-server-guide.md § Identity).
:func:`ticket_subject` redeems it over the auth socket; redemption consumes it and returns the
authoritative `(email, profile)`. A missing, expired or reused ticket refuses the session, and
so does one whose e-mail's :func:`~solver.auth.identity.system_slug` differs from the forking
instance's `EULER_USER_SLUG` pin — that instance *is* the user's own uid, so a ticket for
another user means misrouting or a bypass. Nothing env-carried is the credential: a ticket is
the only thing that survives replay from a sibling process's `/proc/<pid>/environ`.

The spent ticket is scrubbed from the environment, so the shell's children do not inherit it.
A `solver` they run is a plain solver shell: under this uid it resolves from the OS login,
whose role the root-owned policy gives as the e-mail's own (:mod:`solver.auth.identity`).
"""
from __future__ import annotations

__all__ = ['SLUG_PIN_ENV', 'TICKET_ENV', 'ticket_subject']

import os

from solver.auth import Subject
from solver.auth.identity import system_slug

#: Environment variable carrying the one-time shell ticket (set by the user service).
TICKET_ENV: str = 'SOLVER_TICKET'
#: The per-user instance's own system slug (`EULER_USER_SLUG=%i`), exported to the PTY child.
SLUG_PIN_ENV: str = 'EULER_USER_SLUG'


def _redeem(ticket: str) -> tuple[str, str]:
    """Redeem *ticket* at the auth service; `(email, profile)`, or :class:`SystemExit`."""
    from solver.config.env import load_spec
    from euler_site.auth.client import request
    socket_path = load_spec('auth').raw('socket_path')
    try:
        status, data = request(socket_path, 'POST', '/shell-ticket/redeem', body={'ticket': ticket})
    except OSError as exc:
        raise SystemExit(f'identity: auth service unreachable ({exc})') from None
    if status != 200 or not isinstance(data, dict):
        raise SystemExit('identity: shell ticket rejected')
    email, profile = str(data.get('email', '')), str(data.get('profile', ''))
    if not email or not profile:
        raise SystemExit('identity: malformed ticket redemption')
    return email, profile


def ticket_subject() -> Subject:
    """The web shell's :class:`Subject`, from its one-time ticket; refuses the session without one."""
    ticket = os.environ.pop(TICKET_ENV, '').strip()
    if not ticket:
        raise SystemExit(f'identity: the web shell needs a shell ticket (${TICKET_ENV}) — refusing to start')
    email, profile = _redeem(ticket)
    slug = system_slug(email)
    pin = os.environ.get(SLUG_PIN_ENV, '').strip()
    if pin and slug != pin:
        raise SystemExit(f'identity: ticket user {slug!r} does not match this instance ({pin!r}) — refusing to start')
    return Subject(user=email, slug=slug, channel='web', auth_method='shell-ticket', profile=profile)
