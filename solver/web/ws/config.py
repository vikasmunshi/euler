#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Web-shell service runtime configuration, read from the environment.

Like :class:`~solver.web.site.config.SiteConfig`, every value has an env override
so the service runs unprivileged (TCP, scratch sockets) for local testing, and it
never imports :mod:`solver.config` — the *service* has no shell identity; only the
PTY children it forks resolve one, from their ticket. The deployed template unit
sets ``EULER_PROFILE=%i`` and ``EULER_WS_SOCKET=/run/euler/ws-%i.sock`` per
instance.
"""
from __future__ import annotations

__all__ = ['WsConfig']

import os
import sys
from pathlib import Path
from typing import NamedTuple

from solver.web.auth import AUTH_SOCKET_ENV, DEFAULT_AUTH_SOCKET


class WsConfig(NamedTuple):
    """Resolved runtime configuration for one web-shell service process."""

    #: The public unix socket (Caddy upstream). Ignored when serving over TCP (dev).
    socket_path: Path
    #: Group given connect() on the socket (Caddy + the app tier).
    socket_group: str
    #: ``host:port`` for a dev TCP listener instead of the unix socket ('' = socket).
    tcp_bind: str
    #: The profile this instance is *born* as (``EULER_PROFILE=%i``).
    #: When set, a request whose ``X-Profile`` differs is refused — the code-side
    #: backstop to Caddy's per-profile routing — and it is exported to the PTY
    #: child, whose redeemed ticket profile must match it. Empty (dev)
    #: accepts any known profile.
    profile: str
    #: The auth service's public socket — shell-ticket minting.
    auth_socket: str
    #: The command a PTY child execs (the interactive solver shell). Overridable
    #: only in code (tests fork a stub instead of the full shell).
    shell_argv: tuple[str, ...]
    #: Seconds a shell may sit with zero attached sockets before the reaper closes
    #: it (hygiene, not security; 0 disables).
    detached_ttl: int

    @classmethod
    def from_env(cls) -> WsConfig:
        """Build the configuration from the process environment (all optional)."""
        return cls(
            socket_path=Path(os.environ.get('EULER_WS_SOCKET', '/run/euler/ws.sock')),
            socket_group=os.environ.get('EULER_WEB_GROUP', 'euler-web'),
            tcp_bind=os.environ.get('EULER_WS_TCP', '').strip(),
            profile=os.environ.get('EULER_PROFILE', '').strip(),
            auth_socket=os.environ.get(AUTH_SOCKET_ENV, DEFAULT_AUTH_SOCKET),
            shell_argv=(sys.executable, '-m', 'solver'),
            detached_ttl=int(os.environ.get('EULER_WS_DETACHED_TTL', '86400') or '0'),
        )
