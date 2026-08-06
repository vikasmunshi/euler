#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Per-user service runtime configuration, read from the environment.

Union of what the content tier needs (:class:`~solver.web.site.config.SiteConfig`)
and the web shell needs (:class:`~solver.web.ws.config.WsConfig`), plus the one field
that defines the instance: :attr:`slug` (`EULER_USER_SLUG=%i`) — *whose* uid this
process is. Like its predecessors it takes only the `repo_root()` anchor from
:mod:`solver.config.paths` and never the shell's identity; every value
has an env override so the whole service runs unprivileged in a scratch dir for tests.
The deployed `euler-user@<slug>` unit sets `EULER_USER_SLUG` and points
`EULER_REPO_ROOT` at that user's `~/euler` clone.
"""
from __future__ import annotations

__all__ = ['UserConfig']

import sys
from pathlib import Path
from typing import NamedTuple, get_type_hints

from solver.config.env import load_spec
from solver.config.paths import repo_root as find_repo_root
from solver.web.site.config import SiteConfig


class UserConfig(NamedTuple):
    """Resolved runtime configuration for one per-user service process."""

    #: The repo working tree this user's instance reads (their own `~/euler` clone).
    repo_root: Path
    #: The static content root (assets + vendored JS; Caddy serves them in prod).
    static_dir: Path
    #: The public unix socket (Caddy upstream: `/run/euler/user-<slug>.sock`). Ignored
    #: when a listener fd is passed by systemd socket activation, or when serving over TCP.
    socket_path: Path
    #: Group given connect() on the socket (Caddy + the app tier).
    socket_group: str
    #: `host:port` for a dev TCP listener instead of the unix socket ('' = socket).
    tcp_bind: str
    #: Serve /assets and /vendor from the app (dev only; Caddy serves them in prod).
    serve_static: bool
    #: **This instance's own user** — the `system_slug` of the collaborator whose uid
    #: it runs as (`EULER_USER_SLUG`). The identity guard refuses any request whose
    #: `X-User` maps to a different slug (misrouting/bypass), and it is the PTY child's
    #: pin. Empty (dev) accepts any authenticated user.
    slug: str
    #: The auth service's public socket — shell-ticket minting + teardown.
    auth_socket: str
    #: The command a PTY child execs (the interactive solver shell).
    shell_argv: tuple[str, ...]
    #: Seconds a shell may sit with zero attached sockets before the reaper closes it
    #: (hygiene, not security; 0 disables).
    detached_ttl: int = 86400
    #: Base URL of the repo on GitHub, for the problem page's source link.
    github_url: str = 'https://github.com/vikasmunshi/euler'
    #: The branch those source links point at.
    github_branch: str = 'master'

    def site_config(self) -> SiteConfig:
        """The content-tier view of this config (what the reused site handlers read)."""
        return SiteConfig(
            repo_root=self.repo_root, static_dir=self.static_dir,
            socket_path=self.socket_path, socket_group=self.socket_group,
            tcp_bind=self.tcp_bind, serve_static=self.serve_static, profile='',
            github_url=self.github_url, github_branch=self.github_branch)

    @classmethod
    def from_env(cls) -> UserConfig:
        """Build the configuration from the process environment (`[user]` in `env.conf`).

        Three settings are not the table's to give. `repo_root` is *discovered* —
        EULER_REPO_ROOT first (every deployed unit sets it), then
        `solver.config.paths.repo_root`, which refuses to invent a root rather than
        silently adopting site-packages as one. `static_dir` defaults to a path inside
        whatever tree that turns out to be. And the socket's default name embeds the
        slug, which is only known once the environment has been read.
        """
        values = load_spec('user').read(get_type_hints(cls))
        repo_root = find_repo_root()
        slug: str = values.get('slug', '')
        default_socket = f'/run/euler/user-{slug}.sock' if slug else '/run/euler/user.sock'
        values.setdefault('socket_path', Path(default_socket))
        config = cls(repo_root=repo_root,
                     static_dir=values.pop('static_dir', repo_root / 'solver/web/content'),
                     shell_argv=(sys.executable, '-m', 'solver'), **values)
        return config._replace(github_url=config.github_url.rstrip('/'))
