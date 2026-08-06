#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Web-shell service runtime configuration, read from the environment.

Like :class:`~solver.web.site.config.SiteConfig`, every value has an env override
so the service runs unprivileged (TCP, scratch sockets) for local testing, and it
never imports :mod:`solver.config` — the *service* has no shell identity; only the
PTY children it forks resolve one, from their ticket. The deployed template unit
sets `EULER_PROFILE=%i` and `EULER_WS_SOCKET=/run/euler/ws-%i.sock` per
instance.
"""
from __future__ import annotations

__all__ = ['WsConfig']

import sys
from pathlib import Path
from typing import NamedTuple, get_type_hints

from solver.config.env import load_spec


class WsConfig(NamedTuple):
    """Resolved runtime configuration for one web-shell service process."""

    #: The public unix socket (Caddy upstream). Ignored when serving over TCP (dev).
    socket_path: Path
    #: Group given connect() on the socket (Caddy + the app tier).
    socket_group: str
    #: `host:port` for a dev TCP listener instead of the unix socket ('' = socket).
    tcp_bind: str
    #: The profile this instance is *born* as (`EULER_PROFILE=%i`).
    #: When set, a request whose `X-Profile` differs is refused — the code-side
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
    #: it (hygiene, not security; 0 or empty disables).
    detached_ttl: int = 86400

    @classmethod
    def from_env(cls) -> WsConfig:
        """Build the configuration from the process environment (`[ws]` in `env.conf`).

        `shell_argv` has no variable behind it: it is this interpreter, and overriding it
        is a thing tests do in code (forking a stub), not a thing a deployment sets.
        """
        return cls(shell_argv=(sys.executable, '-m', 'solver'),
                   **load_spec('ws').read(get_type_hints(cls)))
