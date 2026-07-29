#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The message spool: user↔staff threads, on its own uid (web-server-guide § Messaging).

Three flows, and only three — any user → staff (``maintainer``+), staff → named
users, staff → everyone. There is **no user↔user leg**: every message has staff at
one end, which makes this a helpdesk plus an announcements board rather than chat.

Why a separate service rather than routes on the auth service: the spool holds
attacker-authored free text by design, and auth holds the SRP verifier database, the
session table and the ticket mint. The same rule that keeps the Gmail credentials in
``euler-smtp`` applies in reverse — an untrusted-input surface lives *away* from the
secrets it has no business near. So this package imports **nothing** from
:mod:`solver.web.auth`; the shared unix-socket client and JSON store live at
:mod:`solver.web.unixhttp` / :mod:`solver.web.store` instead.

It is reachable only over its unix sockets, never routed by Caddy, and authenticates
by ``SO_PEERCRED`` against ``authorizations.json`` — so it needs no session cookie, no
bearer token on the hot path, and no contact with the auth service at all.

Import discipline, as in :mod:`solver.web.auth`: this ``__init__`` and the
``commands`` module stay **stdlib-only importable** (the shell imports them in a base
install with no aiohttp); ``app``/``store``/``identity``/``__main__`` are the service
side and run from the deployed ``/opt/euler`` venv.
"""
from __future__ import annotations

__all__ = ['ADMIN_SOCKET_ENV', 'DEFAULT_ADMIN_SOCKET', 'DEFAULT_MSG_SOCKET', 'KEY_REQUEST_SUBJECT',
           'MSG_SOCKET_ENV']

#: The subject a key-authorization request is filed under — the one message *kind* the
#: spool carries that another command can work. It lives here, with the socket paths,
#: because it is a wire convention between three parties that must not drift: `user`
#: files it (:mod:`solver.crypto.keys`), `user-authorize <id>` requires it before reading
#: a public key out of a body, and the header's message chip offers the Authorize verb on
#: the rows that carry it. Anything else in the spool is prose for a person to read.
KEY_REQUEST_SUBJECT: str = 'Key authorization request from '

#: Env var naming the public spool socket (the per-user service and the shell read it).
MSG_SOCKET_ENV: str = 'EULER_MSG_SOCKET'
#: Env var naming the local admin socket (the staff terminal path reads it).
ADMIN_SOCKET_ENV: str = 'EULER_MSG_ADMIN_SOCKET'
#: Production socket paths, overridable via the env vars above. The public socket joins
#: the shared ``/run/euler`` fabric (``euler-web``-only, which the operator's own uid
#: deliberately is not). The admin socket sits in this service's **own** runtime dir —
#: ``/run/euler-msg``, systemd's ``RuntimeDirectory=`` at ``0700 euler-msg`` — rather
#: than in ``/run/euler-adm``, which is euler-auth-private (``0750 euler-auth``) and
#: therefore not writable by this service. Each admin plane owning its own directory is
#: also the better shape: root traverses either, and nothing else traverses both.
DEFAULT_MSG_SOCKET: str = '/run/euler/msg.sock'
DEFAULT_ADMIN_SOCKET: str = '/run/euler-msg/admin.sock'
