#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Message-service runtime configuration, read from the environment.

The service runs as `euler-msg` from the `/opt/euler` system venv and reads its
scoped `/etc/euler/msg.env` (via the unit's `EnvironmentFile=`) — never the repo
owner's `~/.euler/env` and **never** :mod:`solver.config` (which resolves the shell's
identity and repo paths this service user cannot read). Every value has an env override
so the whole service can run unprivileged in a scratch dir for local testing.

Unlike the auth service there is no mail relay and no base URL here: the spool sends
no e-mail and renders no links (web-server-guide § Messaging — *No mail*), which is
what lets the unit run `AF_UNIX`-only.
"""
from __future__ import annotations

__all__ = ['MsgConfig']

from pathlib import Path
from typing import NamedTuple, get_type_hints

from solver.config.env import load_spec


class MsgConfig(NamedTuple):
    """Resolved runtime configuration for one message-service process."""

    #: The euler-msg-private state dir holding `messages.json`.
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
    #: The directory holding the per-user instance sockets (`user-<slug>.sock`): the
    #: delivery nudge targets the recipient's one socket. Empty disables the push (a
    #: deploy with no web tier, or a test that does not exercise it).
    user_socket_dir: str = ''

    @classmethod
    def from_env(cls) -> MsgConfig:
        """Build the configuration from the process environment (`[msg]` in `env.conf`).

        `EULER_MSG_ADMIN_TOKEN` is marked `!required` there (the deployed `msg.env`
        provides it); everything else has a production default.
        """
        return cls(**load_spec('msg').read(get_type_hints(cls)))
