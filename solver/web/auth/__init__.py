#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Web authentication: the auth service and its clients (DD-6/DD-7/DD-9).

SRP-6a credential verification, sessions, remember-me, invite/OTP registration
state, one-time shell tickets, and the local admin plane — the service is the
sole reader/writer of all of it, under ``/var/lib/euler-auth``.

Kept wholly separate from ``solver.crypto`` (solution encryption): this package
gates web access and shares no key material with the encryption master key.

Import discipline: this ``__init__`` (and the ``client``/``commands``/``policy``
modules) must stay **stdlib-only importable** — the shell imports them in a base
install with no aiohttp. The service side (``app``, ``__main__``) imports aiohttp
and runs only from the deployed ``/opt/euler`` venv (DD-5).
"""
from __future__ import annotations

__all__ = ['AUTH_SOCKET_ENV', 'ADMIN_SOCKET_ENV', 'DEFAULT_AUTH_SOCKET', 'DEFAULT_ADMIN_SOCKET']

#: Env var naming the public auth socket (ticket redemption reads it — DD-9).
AUTH_SOCKET_ENV: str = 'EULER_AUTH_SOCKET'
#: Env var naming the local admin socket (the admin CLI reads it — DD-6).
ADMIN_SOCKET_ENV: str = 'EULER_AUTH_ADMIN_SOCKET'
#: Production socket paths (DD-1/DD-6), overridable via the env vars above. The
#: admin socket lives in its own ``euler-auth``-private runtime dir (0600 —
#: the admin plane is **wheel-gated**: only root, via sudo, reaches it); the
#: shared ``/run/euler`` is ``euler-web``-only, which operators are not.
DEFAULT_AUTH_SOCKET: str = '/run/euler/auth.sock'
DEFAULT_ADMIN_SOCKET: str = '/run/euler-adm/auth-admin.sock'
