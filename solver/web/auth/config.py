#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth-service runtime configuration, read from the environment.

The service runs as `euler-auth` from the `/opt/euler` system venv and reads its scoped
`/etc/euler/auth.env` (via the unit's `EnvironmentFile=`) — never the repo owner's
`~/.euler/env`, and never a `Config`: it has no working tree, so resolving one would raise
at import and take the service down before it could signal readiness. Which variable
carries each setting, and what it is without one, is the `[auth]` section of
`solver/config/env.conf`; this class declares the shape and does the normalising that a
table cannot. Every value has an env override, so the whole service runs unprivileged in
a scratch dir for local testing.
"""
from __future__ import annotations

__all__ = ['AuthConfig']

from pathlib import Path
from typing import NamedTuple, get_type_hints

from solver.config.env import load_spec


class AuthConfig(NamedTuple):
    """Resolved runtime configuration for one auth-service process."""

    #: The euler-auth-private state dir: users.json / pending.json / remember.json / session-secret.
    state_dir: Path
    #: The public unix socket (Caddy upstream + shell-ticket redemption).
    socket_path: Path
    #: The local admin-plane unix socket (never routed through Caddy).
    admin_socket_path: Path
    #: Group given connect() on the public socket (Caddy + the app tier).
    socket_group: str
    #: Group for the admin socket — empty means **private** (0600, euler-auth
    #: only): the admin plane is wheel-gated, root connects via sudo.
    admin_socket_group: str
    #: Shared secret for the admin API (second factor beside the socket's group gate).
    admin_token: str
    #: Public base URL (https://<FQDN>) used in invite / reset links.
    base_url: str
    #: host:port of the loopback mail relay — the only mail path out.
    smtp_relay: str
    #: Version tag of the Terms of use the registration flow records.
    terms_version: str
    #: Where invite-request notices go (the login page's "Request an invite" form).
    #: Empty disables the notice — the `requests.json` queue is the system of record,
    #: so a missing address costs a nudge, not a request.
    owner_email: str = ''
    #: The directory holding the per-user instance sockets (`user-<slug>.sock`): the
    #: teardown push targets the one socket for the affected user. Empty
    #: disables the push (a deploy with no web tier, or a test that does not exercise it)
    #: — the default, so `from_env` is the only place the real directory is set.
    user_socket_dir: str = ''

    @classmethod
    def from_env(cls) -> AuthConfig:
        """Build the configuration from the process environment (`[auth]` in `env.conf`).

        `EULER_ADMIN_TOKEN` and `EULER_BASE_URL` are marked `!required` there, so an
        unset one exits at startup naming itself; everything else has a production default.
        """
        config = cls(**load_spec('auth').read(get_type_hints(cls)))
        return config._replace(base_url=config.base_url.rstrip('/'),
                               owner_email=config.owner_email.lower())
