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
   so does one whose e-mail's :func:`system_slug` differs from the forking
   instance's ``EULER_USER_SLUG`` pin (MT-4/MT-7 — that instance *is* the user's
   own uid, so a ticket for another user means misrouting or a bypass). Nothing
   env-carried is the credential — a ticket is the only thing that survives replay
   from a sibling process's ``/proc/<pid>/environ``. In the per-user model the web
   channel is **not capped** (MT-10a): an ``admin`` account is web-reachable, its
   authority contained by its own uid + SRP, not by the channel.
2. **Instance identity** — a ``euler-user-<slug>`` per-user service uid whose
   ticketed shell has already redeemed and scrubbed the one-time ticket (MT-4):
   the descendant ``solver`` processes it spawns (claude-solve's headless Claude,
   a nested ``solver "…"``) carry no ticket and resolve from the instance itself.
   The uid *is* the collaborator; the handed-down ``EULER_USER_EMAIL`` is trusted
   only when :func:`system_slug` maps it back to the uid's own ``EULER_USER_SLUG``
   pin, and the profile still comes from policy — so a child cannot forge either a
   different identity or a higher rung. Any *other* ``euler-*`` uid still aborts.
3. **Local terminal** — the OS login's profile from the ``users`` map
   (DD-12); the **checkout owner floors to ``admin``** when unlisted (you cannot
   lock yourself out), an explicit entry wins, and a real non-owner login without
   an entry is ``contributor``. A ``euler-*`` service uid that is neither a
   ticketed web shell nor a properly-pinned per-user instance **aborts**, so a
   ``reader`` web shell cannot ``unset SOLVER_TICKET`` and re-exec ``solver`` to
   escalate — its uid pins the identity, and the profile follows from policy.

Absorbs the former ``solver.utils.identity``. Stdlib-only and free of any
``solver.config`` dependency (config imports this during construction); ticket
redemption lazily imports the equally-stdlib ``solver.web.auth.client``.
"""
from __future__ import annotations

__all__ = ['resolve_subject', 'slugify', 'system_slug', 'TICKET_ENV', 'INSTANCE_EMAIL_ENV']

import getpass
import hashlib
import os
import re
from pathlib import Path

from solver.auth.authorizations import Authorizations
from solver.auth.subject import LADDER, Subject

#: Environment variable carrying the one-time shell ticket (set by the user service).
TICKET_ENV: str = 'SOLVER_TICKET'
#: The per-user instance's own system slug (``EULER_USER_SLUG=%i``), exported to the
#: PTY child: the redeemed ticket's e-mail must map to it (:func:`system_slug`), else the
#: shell aborts — the instance *is* that user's uid, so a mismatch is misrouting (MT-4/MT-7).
SLUG_PIN_ENV: str = 'EULER_USER_SLUG'
#: The bound e-mail of a per-user instance, handed *down* the process tree by a shell that
#: has already redeemed its ticket (:func:`resolve_subject` scrubs the one-time ticket and
#: exports this in its place). Descendant ``solver`` processes — claude-solve's headless
#: Claude, a nested ``solver "…"`` — resolve identity from it via the **instance-identity
#: plane**. Not a credential: it is trusted only when :func:`system_slug` maps it back to
#: the uid's own :data:`SLUG_PIN_ENV`, so a child cannot forge a different user past it.
INSTANCE_EMAIL_ENV: str = 'EULER_USER_EMAIL'
#: Service accounts are named ``euler-*``; such a uid with no ticket must abort. (The
#: per-user instances are ``euler-user-<slug>`` — they never resolve identity themselves;
#: only the ticketed PTY children they fork do, and a ticket is present there.)
_SERVICE_PREFIX: str = 'euler-'

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


def _instance_identity(os_login: str, authz: Authorizations) -> Subject | None:
    """Resolve a per-user service uid to its bound collaborator, ticket-free (MT-4).

    The **instance-identity plane**: a ``euler-user-<slug>`` uid is provisioned for
    exactly one collaborator, and its ticketed PTY shell scrubs the one-time ticket
    once redeemed. The descendant ``solver`` processes that shell spawns —
    claude-solve's headless Claude, a nested ``solver "…"`` — therefore have *no*
    ticket; they re-resolve here instead of aborting.

    Trust is the OS uid, cross-checked three ways: the account is
    ``euler-user-<pin>``, the handed-down :data:`INSTANCE_EMAIL_ENV` maps back to
    ``<pin>`` under :func:`system_slug`, and the pin is present. The e-mail is an
    env value a child could rewrite — but only a value whose ``system_slug`` equals
    this uid's own pin survives, i.e. the instance's own user, so it cannot forge a
    different identity. The **profile** comes from the same policy the auth service
    reads (``authorizations.json``), never from the environment, so a child cannot
    forge a higher rung; an unlisted user floors to the weakest rung. Returns
    ``None`` when this is not a properly-pinned per-user instance (any other
    ``euler-*`` account), so the caller still aborts.
    """
    email = os.environ.get(INSTANCE_EMAIL_ENV, '').strip()
    pin = os.environ.get(SLUG_PIN_ENV, '').strip()
    if not email or not pin or os_login != f'euler-user-{pin}' or system_slug(email) != pin:
        return None
    profile = authz.profile_for(email) or LADDER[0]  # unlisted → least privilege (fail closed low)
    return Subject(user=email, slug=pin, channel='web', auth_method='instance-identity', profile=profile)


def resolve_subject(root_dir: Path, authz: Authorizations | None = None) -> Subject:
    """Resolve the current :class:`Subject` (identity + profile).

    *authz* is the loaded policy; if omitted it is loaded (deployed SoR → built-in
    default). Raises :class:`SystemExit` when no identity plane matches.
    """
    if authz is None:
        authz = Authorizations.load()

    ticket = os.environ.get(TICKET_ENV, '').strip()
    if ticket:
        email, profile = _redeem_ticket(ticket)     # authoritative (email, profile); admin uncapped (MT-10a)
        slug = system_slug(email)
        pin = os.environ.get(SLUG_PIN_ENV, '').strip()
        if pin and slug != pin:
            # The forking instance *is* this user's uid (euler-user-<pin>, MT-4/MT-7):
            # a ticket for another user means misrouting or a bypass attempt, and this
            # process — with that uid's home, keys, and clone — must not run as them.
            raise SystemExit(f'identity: ticket user {slug!r} does not match '
                             f'this instance ({pin!r}) — refusing to start')
        return Subject(user=email, slug=slug, channel='web',
                       auth_method='shell-ticket', profile=profile)

    try:
        os_login = getpass.getuser()
    except OSError:
        raise SystemExit('identity: could not determine the OS login') from None
    if os_login.startswith(_SERVICE_PREFIX):
        subject = _instance_identity(os_login, authz)
        if subject is not None:
            return subject
        raise SystemExit(f'identity: service account {os_login!r} has no shell ticket — refusing to start')

    is_owner = _owns_checkout(root_dir)
    mapped = authz.profile_for(os_login)             # unlisted → owner floors to admin, else contributor
    profile = mapped if mapped is not None else ('admin' if is_owner else 'contributor')
    return Subject(user=os_login, slug=slugify(os_login), channel='terminal',
                   auth_method='checkout-owner' if is_owner else 'os-login', profile=profile)
