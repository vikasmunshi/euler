#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Ambient user identity **and profile**: who is this shell running as (DD-9).

Resolution yields ``(display, slug, profile)``, resolved **once** at startup.
Two identity planes, each with an explicit voucher (docs/server-redesign.md,
DD-9); there is no anonymous fallback:

1. **Web shell** — ``SOLVER_TICKET`` in the environment: a **one-time shell
   ticket** minted by the auth service against the user's live session (the ws
   service forwards the session cookie at WS attach) and redeemed here over the
   auth service's public socket. Redemption consumes the ticket and returns the
   authoritative ``(email, profile)``; a missing/expired/reused ticket aborts
   startup. Nothing env-carried is the credential — ``/proc/<pid>/environ`` is
   same-uid-readable across every web shell (they all run as ``euler-ws``), so
   only a consumable ticket prevents one web user replaying another's identity.
2. **Local terminal** — the process uid **owns the repo checkout**: physical /
   login access to the checkout is the trust, stated exactly. Grants the
   ``admin`` profile under the OS login name. Service uids never fall through
   to admin — a bare ``solver`` inside a web PTY (uid ``euler-ws``) resolves
   neither plane and exits.

``SOLVER_USER`` is **display-only** where the ws service sets it; it grants
nothing and is not read here. The old assume-an-identity inputs
(``SOLVER_USER`` / ``keys/.user-email`` / ``keys/.env``) are gone: the user DB
is ``euler-auth``-private (DD-6), so there is nothing local to verify an
explicit identity against — exercising a lesser profile is done through a real
web login.

``display`` keys per-user shell state (history, last problem) via ``slug``;
``profile`` (``admin`` / ``user`` / ``guest``) drives **command authorization**
(see :mod:`solver.shell.command`). Confidentiality proper (web login, solution
encryption) is enforced elsewhere — SRP in :mod:`solver.web.auth` and the
git-filter master key in :mod:`solver.crypto`; this module only resolves the
*identity and profile* those tiers vouch for.

It lives under :mod:`solver.utils` (an empty-``__init__`` package) rather than
``solver.shell`` so :mod:`solver.config` can import it during construction
without triggering the shell package's own import of ``solver.config``. Module
import is stdlib-only; ticket redemption lazily imports the (equally
stdlib-only) :mod:`solver.web.auth.client`.
"""
from __future__ import annotations

__all__ = ['resolve_identity', 'slugify']

import getpass
import hashlib
import os
import re
from pathlib import Path

#: Environment variable carrying the one-time shell ticket (set by the ws service).
TICKET_ENV: str = 'SOLVER_TICKET'

#: Characters kept verbatim in a slug; everything else becomes ``_``.
_SLUG_KEEP = re.compile(r'[^a-z0-9._-]+')


def slugify(identity: str) -> str:
    """Return a filesystem-safe directory name for *identity*.

    Lower-cases, collapses any run of characters outside ``[a-z0-9._-]`` to a
    single ``_``, and appends a short hash of the raw identity so two distinct
    identities can never collide onto the same slug (e.g. ``a@x``/``a_x``).
    """
    base = _SLUG_KEEP.sub('_', identity.strip().lower()).strip('_.')
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()[:6]
    return f'{base}-{digest}'


def _redeem_ticket(ticket: str) -> tuple[str, str]:
    """Redeem the one-time shell ticket at the auth service; ``(email, profile)``.

    Any failure — service down, ticket unknown/expired/already redeemed — raises
    :class:`SystemExit`: an unvouched web shell must not start.
    """
    from solver.web.auth import AUTH_SOCKET_ENV, DEFAULT_AUTH_SOCKET
    from solver.web.auth.client import request
    socket_path = os.environ.get(AUTH_SOCKET_ENV, DEFAULT_AUTH_SOCKET)
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


def resolve_identity(root_dir: Path) -> tuple[str, str, str]:
    """Resolve the current user, returning ``(display, slug, profile)``.

    *display* is the raw identity for prompts/logs; *slug* is its filesystem-safe
    form for per-user state directories; *profile* (``admin``/``user``/``guest``)
    drives command authorization. See the module docstring for the two identity
    planes; anything that matches neither raises :class:`SystemExit`.
    """
    ticket = os.environ.get(TICKET_ENV, '').strip()
    if ticket:
        email, profile = _redeem_ticket(ticket)
        return email, slugify(email), profile
    try:
        if os.getuid() == root_dir.stat().st_uid:
            display = getpass.getuser()
            return display, slugify(display), 'admin'
    except OSError:
        pass
    raise SystemExit('identity: not the checkout owner and no shell ticket — refusing to start')
