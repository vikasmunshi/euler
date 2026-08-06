#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Web authentication: the auth service and its clients.

SRP-6a credential verification, sessions, remember-me, invite/OTP registration
state, one-time shell tickets, and the local admin plane — the service is the
sole reader/writer of all of it, under `/var/lib/euler-auth`.

Kept wholly separate from `solver.crypto` (solution encryption): this package
gates web access and shares no key material with the encryption master key.

Import discipline: this `__init__` (and the `client`/`commands`/`policy`
modules) must stay **stdlib-only importable** — the shell imports them in a base
install with no aiohttp. The service side (`app`, `__main__`) imports aiohttp
and runs only from the deployed `/opt/euler` venv.
"""
from __future__ import annotations

#: This package exports nothing. The socket paths and the variables that override them
#: used to live here as four constants; they are settings, and settings live in one
#: table — `[auth]` in `solver/config/env.conf`, read through
#: :func:`solver.config.env.load_spec`. The admin socket's own `euler-auth`-private
#: runtime dir (0600 — the admin plane is **wheel-gated**: only root, via sudo, reaches
#: it) is documented there, beside the value that implements it; the shared `/run/euler`
#: is `euler-web`-only, which operators are not.
__all__: list[str] = []
