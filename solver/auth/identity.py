#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Identity resolution → a :class:`~solver.auth.subject.Subject` (DD-9/DD-12).

Resolves *who* this process runs as and *what* it may do, **once** at startup,
across the identity planes (docs/secure-web-server.md, DD-9/DD-12). There is no
anonymous fallback; a process that matches no plane exits.

1. **Web shell** — ``SOLVER_TICKET`` in the environment: a **one-time shell
   ticket** minted by the auth service against the user's live session and
   redeemed here over the auth socket. Redemption consumes it and returns the
   authoritative ``(email, profile)``; a missing/expired/reused ticket aborts, and
   so does one whose profile differs from the forking instance's
   ``EULER_PROFILE`` pin (DD-13 — that instance *is* the rung's uid). Nothing
   env-carried is the credential — ``/proc/<pid>/environ`` is same-uid-readable
   across every web shell on a rung (all ``euler-ws-<profile>``), so only a
   consumable ticket prevents replay. The web channel is **capped at
   ``maintainer``** (``admin`` is local-only, DD-11).
2. **Local terminal** — the OS login's profile from the ``users`` map
   (DD-12); the **checkout owner floors to ``admin``** when unlisted (you cannot
   lock yourself out), an explicit entry wins, and a real non-owner login without
   an entry is ``contributor``. A ``euler-*`` service uid **without** a ticket
   aborts, so a ``reader`` web shell cannot ``unset SOLVER_TICKET`` and re-exec
   ``solver`` to escalate.

Absorbs the former ``solver.utils.identity``. Stdlib-only and free of any
``solver.config`` dependency (config imports this during construction); ticket
redemption lazily imports the equally-stdlib ``solver.web.auth.client``.
"""
from __future__ import annotations

__all__ = ['resolve_subject', 'slugify', 'system_slug', 'TICKET_ENV']

import getpass
import hashlib
import os
import re
from pathlib import Path

from solver.auth.authorizations import Authorizations
from solver.auth.subject import Subject

#: Environment variable carrying the one-time shell ticket (set by the ws service).
TICKET_ENV: str = 'SOLVER_TICKET'
#: The per-profile ws instance's own profile (``EULER_PROFILE=%i``), exported to the
#: PTY child: the redeemed ticket's profile must equal it, else the shell aborts (DD-13).
PROFILE_PIN_ENV: str = 'EULER_PROFILE'
#: Service accounts are named ``euler-*``; such a uid with no ticket must abort.
_SERVICE_PREFIX: str = 'euler-'
#: Web accounts never exceed this profile (``admin`` is local-only, DD-11).
_WEB_CAP: str = 'maintainer'

_SLUG_KEEP = re.compile(r'[^a-z0-9._-]+')
_SYSTEM_SLUG_STRIP = re.compile(r'[^a-z0-9]+')
#: Cap on the sanitised local-part so ``euler-user-<slug>`` stays well under the
#: system name limit (``euler-user-`` + ≤13 + ``-`` + 6-hex ≈ 31 chars).
_SYSTEM_LOCALPART_MAX: int = 12


def slugify(identity: str) -> str:
    """Return a filesystem-safe directory name for *identity* (per-user state dirs).

    Lower-cases, collapses any run of characters outside ``[a-z0-9._-]`` to a
    single ``_``, and appends a short hash of the raw identity so two distinct
    identities can never collide onto the same slug (e.g. ``a@x``/``a_x``). Used
    for terminal identities; the web/system identity uses :func:`system_slug`.
    """
    base = _SLUG_KEEP.sub('_', identity.strip().lower()).strip('_.')
    digest = hashlib.sha1(identity.encode('utf-8')).hexdigest()[:6]
    return f'{base}-{digest}'


def system_slug(identity: str) -> str:
    """Return a **system-account** slug for *identity* — the per-user uid/home/socket name (MT-14).

    Stricter than :func:`slugify`: the result matches ``^[a-z][a-z0-9-]*$`` (no ``.`` or ``_``), so
    ``useradd``'s ``NAME_REGEX`` accepts ``euler-user-<slug>``. Built from the sanitised, truncated
    e-mail local-part plus a short hash of the normalised identity — the hash keeps distinct
    identities from colliding even when their local-parts sanitise to the same prefix. The e-mail
    remains the login identity; this is only its derived system name.
    """
    normalized = identity.strip().lower()
    localpart = normalized.split('@', 1)[0]
    base = _SYSTEM_SLUG_STRIP.sub('-', localpart).strip('-')[:_SYSTEM_LOCALPART_MAX].strip('-')
    if not base or not base[0].isalpha():
        base = f'u{base}'                            # force a letter start (useradd NAME_REGEX)
    digest = hashlib.sha1(normalized.encode('utf-8')).hexdigest()[:6]
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


def _owns_checkout(root_dir: Path) -> bool:
    """True if the current process uid owns the repo checkout (the local trust anchor)."""
    try:
        return os.getuid() == root_dir.stat().st_uid
    except OSError:
        return False


def resolve_subject(root_dir: Path, authz: Authorizations | None = None) -> Subject:
    """Resolve the current :class:`Subject` (identity + profile + permissions).

    *authz* is the loaded policy; if omitted it is loaded (deployed SoR → built-in
    default). Raises :class:`SystemExit` when no identity plane matches.
    """
    if authz is None:
        authz = Authorizations.load()

    ticket = os.environ.get(TICKET_ENV, '').strip()
    if ticket:
        email, profile = _redeem_ticket(ticket)
        if profile == 'admin':                      # web is capped at maintainer (DD-11)
            profile = _WEB_CAP
        pin = os.environ.get(PROFILE_PIN_ENV, '').strip()
        if pin and profile != pin:
            # The forking ws instance *is* the profile's uid (euler-ws-<pin>, DD-13):
            # a ticket for another rung means misrouting or a bypass attempt, and this
            # process — with that uid's ACLs — must not run as the other rung.
            raise SystemExit(f'identity: ticket profile {profile!r} does not match '
                             f'this instance ({pin!r}) — refusing to start')
        return Subject(user=email, slug=system_slug(email), channel='web',
                       auth_method='shell-ticket', profile=profile,
                       permissions=authz.permissions_for(profile))

    try:
        os_login = getpass.getuser()
    except OSError:
        raise SystemExit('identity: could not determine the OS login') from None
    if os_login.startswith(_SERVICE_PREFIX):
        raise SystemExit(f'identity: service account {os_login!r} has no shell ticket — refusing to start')

    is_owner = _owns_checkout(root_dir)
    mapped = authz.profile_for(os_login)             # unlisted → owner floors to admin, else contributor
    profile = mapped if mapped is not None else ('admin' if is_owner else 'contributor')
    return Subject(user=os_login, slug=slugify(os_login), channel='terminal',
                   auth_method='checkout-owner' if is_owner else 'os-login', profile=profile,
                   permissions=authz.permissions_for(profile))
