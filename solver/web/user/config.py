#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Per-user service runtime configuration, read from the environment (DD-5/MT-4).

Union of what the content tier needs (:class:`~solver.web.site.config.SiteConfig`)
and the web shell needs (:class:`~solver.web.ws.config.WsConfig`), plus the one field
that defines the instance: :attr:`slug` (``EULER_USER_SLUG=%i``) — *whose* uid this
process is. Like its predecessors it never imports :mod:`solver.config`; every value
has an env override so the whole service runs unprivileged in a scratch dir for tests.
The deployed ``euler-user@<slug>`` unit sets ``EULER_USER_SLUG`` and points
``EULER_REPO_ROOT`` at that user's ``~/euler`` clone.
"""
from __future__ import annotations

__all__ = ['UserConfig']

import os
import sys
from pathlib import Path
from typing import NamedTuple

from solver.web.auth import AUTH_SOCKET_ENV, DEFAULT_AUTH_SOCKET
from solver.web.site.config import SiteConfig

#: Repo root as seen from this file (``solver/web/user/config.py`` → up 3): the default
#: working tree for a dev run straight from a checkout.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_GITHUB_URL = 'https://github.com/vikasmunshi/euler'
_GITHUB_BRANCH = 'master'


def _truthy(value: str) -> bool:
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


class UserConfig(NamedTuple):
    """Resolved runtime configuration for one per-user service process."""

    #: The repo working tree this user's instance reads (their own ``~/euler`` clone).
    repo_root: Path
    #: The static content root (assets + vendored JS; Caddy serves them in prod).
    static_dir: Path
    #: The public unix socket (Caddy upstream: ``/run/euler/user-<slug>.sock``). Ignored
    #: when a listener fd is passed by systemd socket activation, or when serving over TCP.
    socket_path: Path
    #: Group given connect() on the socket (Caddy + the app tier).
    socket_group: str
    #: ``host:port`` for a dev TCP listener instead of the unix socket ('' = socket).
    tcp_bind: str
    #: Serve /assets and /vendor from the app (dev only; Caddy serves them in prod).
    serve_static: bool
    #: **This instance's own user** — the ``system_slug`` of the collaborator whose uid
    #: it runs as (``EULER_USER_SLUG``). The identity guard refuses any request whose
    #: ``X-User`` maps to a different slug (misrouting/bypass), and it is the PTY child's
    #: pin. Empty (dev) accepts any authenticated user.
    slug: str
    #: The auth service's public socket — shell-ticket minting + teardown (DD-9).
    auth_socket: str
    #: The command a PTY child execs (the interactive solver shell).
    shell_argv: tuple[str, ...]
    #: Seconds a shell may sit with zero attached sockets before the reaper closes it
    #: (DD-14 hygiene; 0 disables).
    detached_ttl: int
    #: Base URL of the repo on GitHub, for the problem page's source link.
    github_url: str = _GITHUB_URL
    #: The branch those source links point at.
    github_branch: str = _GITHUB_BRANCH

    def site_config(self) -> SiteConfig:
        """The content-tier view of this config (what the reused site handlers read)."""
        return SiteConfig(
            repo_root=self.repo_root, static_dir=self.static_dir,
            socket_path=self.socket_path, socket_group=self.socket_group,
            tcp_bind=self.tcp_bind, serve_static=self.serve_static, profile='',
            github_url=self.github_url, github_branch=self.github_branch)

    @classmethod
    def from_env(cls) -> UserConfig:
        """Build the configuration from the process environment (all optional)."""
        repo_root = Path(os.environ.get('EULER_REPO_ROOT', str(_REPO_ROOT)))
        static_dir = Path(os.environ.get('EULER_CONTENT_STATIC_DIR',
                                         str(repo_root / 'solver/web/content')))
        slug = os.environ.get('EULER_USER_SLUG', '').strip()
        default_socket = f'/run/euler/user-{slug}.sock' if slug else '/run/euler/user.sock'
        return cls(
            repo_root=repo_root,
            static_dir=static_dir,
            socket_path=Path(os.environ.get('EULER_USER_SOCKET', default_socket)),
            socket_group=os.environ.get('EULER_WEB_GROUP', 'euler-web'),
            tcp_bind=os.environ.get('EULER_USER_TCP', '').strip(),
            serve_static=_truthy(os.environ.get('EULER_CONTENT_SERVE_STATIC', '')),
            slug=slug,
            auth_socket=os.environ.get(AUTH_SOCKET_ENV, DEFAULT_AUTH_SOCKET),
            shell_argv=(sys.executable, '-m', 'solver'),
            detached_ttl=int(os.environ.get('EULER_WS_DETACHED_TTL', '86400') or '0'),
            github_url=os.environ.get('EULER_GITHUB_URL', _GITHUB_URL).strip().rstrip('/'),
            github_branch=os.environ.get('EULER_GITHUB_BRANCH', _GITHUB_BRANCH).strip(),
        )
