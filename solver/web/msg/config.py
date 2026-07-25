#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Message-service runtime configuration, read from the environment.

The service runs as ``euler-msg`` from the ``/opt/euler`` system venv and reads its
scoped ``/etc/euler/msg.env`` (via the unit's ``EnvironmentFile=``) — never the repo
owner's ``~/.euler/env`` and **never** :mod:`solver.config` (which resolves the shell's
identity and repo paths this service user cannot read). Every value has an env override
so the whole service can run unprivileged in a scratch dir for local testing.

Unlike the auth service there is no mail relay and no base URL here: the spool sends
no e-mail and renders no links (web-server-guide § Messaging — *No mail*), which is
what lets the unit run ``AF_UNIX``-only.
"""
from __future__ import annotations

__all__ = ['MsgConfig']

import os
from pathlib import Path
from typing import NamedTuple

from solver.web.msg import ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET, DEFAULT_MSG_SOCKET, MSG_SOCKET_ENV


class MsgConfig(NamedTuple):
    """Resolved runtime configuration for one message-service process."""

    #: The euler-msg-private state dir holding ``messages.json``.
    state_dir: Path
    #: The public unix socket: the per-user services and their PTY children.
    socket_path: Path
    #: The local admin unix socket (never routed by Caddy; sudo-only).
    admin_socket_path: Path
    #: Group given connect() on the public socket — every collaborator uid is in it.
    socket_group: str
    #: Group for the admin socket — empty means **private** (0600, euler-msg only):
    #: the admin plane is wheel-gated, root connects via sudo.
    admin_socket_group: str
    #: Shared secret for the admin API (second factor beside the socket's group gate).
    admin_token: str
    #: The directory holding the per-user instance sockets (``user-<slug>.sock``): the
    #: delivery nudge targets the recipient's one socket. Empty disables the push (a
    #: deploy with no web tier, or a test that does not exercise it).
    user_socket_dir: str = ''

    @classmethod
    def from_env(cls) -> MsgConfig:
        """Build the configuration from the process environment.

        ``EULER_MSG_ADMIN_TOKEN`` is required (the deployed ``msg.env`` provides it);
        everything else has a production default.
        """
        admin_token = os.environ.get('EULER_MSG_ADMIN_TOKEN', '').strip()
        if not admin_token:
            raise SystemExit('msg service: EULER_MSG_ADMIN_TOKEN must be set')
        return cls(
            state_dir=Path(os.environ.get('EULER_MSG_STATE_DIR', '/var/lib/euler-msg')),
            socket_path=Path(os.environ.get(MSG_SOCKET_ENV, DEFAULT_MSG_SOCKET)),
            admin_socket_path=Path(os.environ.get(ADMIN_SOCKET_ENV, DEFAULT_ADMIN_SOCKET)),
            socket_group=os.environ.get('EULER_WEB_GROUP', 'euler-web'),
            admin_socket_group=os.environ.get('EULER_ADM_GROUP', ''),
            admin_token=admin_token,
            user_socket_dir=os.environ.get('EULER_USER_SOCKET_DIR', '/run/euler').strip(),
        )
