#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Auth-service runtime configuration, read from the environment (DD-5/DD-6).

The service runs as ``euler-auth`` from the ``/opt/euler`` system venv and reads
its scoped ``/etc/euler/auth.env`` (via the unit's ``EnvironmentFile=``) — never
the repo owner's ``~/.euler/env`` and **never** :mod:`solver.config` (which resolves the
shell's identity and repo paths the service user cannot read). Every value has
an env override so the whole service can run unprivileged in a scratch dir for
local testing.
"""
from __future__ import annotations

__all__ = ['AuthConfig']

import os
from pathlib import Path
from typing import NamedTuple


class AuthConfig(NamedTuple):
    """Resolved runtime configuration for one auth-service process."""

    #: DD-6 state dir: users.json / pending.json / remember.json / session-secret.
    state_dir: Path
    #: The public unix socket (Caddy upstream + shell-ticket redemption).
    socket_path: Path
    #: The local admin-plane unix socket (never routed through Caddy).
    admin_socket_path: Path
    #: Group given connect() on the public socket (Caddy + the app tier).
    socket_group: str
    #: Group for the admin socket — empty means **private** (0600, euler-auth
    #: only): the admin plane is wheel-gated, root connects via sudo (DD-6).
    admin_socket_group: str
    #: Shared secret for the admin API (second factor beside the socket's group gate).
    admin_token: str
    #: Public base URL (https://<FQDN>) used in invite / reset links.
    base_url: str
    #: host:port of the loopback mail relay (DD-8) — the only mail path out.
    smtp_relay: str
    #: Version tag of the Terms of use the registration flow records (DD-7).
    terms_version: str
    #: The directory holding the per-user instance sockets (``user-<slug>.sock``): the
    #: DD-14 teardown push targets the one socket for the affected user (MT-4). Empty
    #: disables the push (a deploy with no web tier, or a test that does not exercise it)
    #: — the default, so ``from_env`` is the only place the real directory is set.
    user_socket_dir: str = ''

    @classmethod
    def from_env(cls) -> AuthConfig:
        """Build the configuration from the process environment.

        ``EULER_ADMIN_TOKEN`` and ``EULER_BASE_URL`` are required (the deployed
        ``auth.env`` provides them); everything else has a production default.
        """
        admin_token = os.environ.get('EULER_ADMIN_TOKEN', '').strip()
        base_url = os.environ.get('EULER_BASE_URL', '').strip().rstrip('/')
        if not admin_token or not base_url:
            raise SystemExit('auth service: EULER_ADMIN_TOKEN and EULER_BASE_URL must be set')
        return cls(
            state_dir=Path(os.environ.get('EULER_AUTH_STATE_DIR', '/var/lib/euler-auth')),
            socket_path=Path(os.environ.get('EULER_AUTH_SOCKET', '/run/euler/auth.sock')),
            admin_socket_path=Path(os.environ.get('EULER_AUTH_ADMIN_SOCKET', '/run/euler-adm/auth-admin.sock')),
            socket_group=os.environ.get('EULER_WEB_GROUP', 'euler-web'),
            admin_socket_group=os.environ.get('EULER_ADM_GROUP', ''),
            admin_token=admin_token,
            base_url=base_url,
            smtp_relay=os.environ.get('EULER_SMTP_RELAY', '127.0.0.1:8025'),
            terms_version=os.environ.get('TERMS_VERSION', '1'),
            user_socket_dir=os.environ.get('EULER_USER_SOCKET_DIR', '/run/euler').strip(),
        )
