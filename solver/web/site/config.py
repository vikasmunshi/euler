#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Content-service runtime configuration, read from the environment.

Like :class:`~solver.web.auth.config.AuthConfig`, every value has an env override
so the service runs unprivileged in a scratch dir for local testing. It takes
`repo_root()` from :mod:`solver.config.paths` — an anchor, computed and side-effect-free
— and nothing else: never the shell's identity, and never a process the service uid did
not ask to have moved. The deployed unit sets these via `EnvironmentFile=` and
one `EULER_PROFILE=<profile>` per template-unit instance.
"""
from __future__ import annotations

__all__ = ['SiteConfig']

from pathlib import Path
from typing import NamedTuple, get_type_hints

from solver.config.env import load_spec
from solver.config.paths import repo_root as find_repo_root


class SiteConfig(NamedTuple):
    """Resolved runtime configuration for one content-service process."""

    #: The repo working tree the service reads (solutions/ · docs/ · solver/web/content/).
    repo_root: Path
    #: The static content root (assets + vendored JS + maintenance page).
    static_dir: Path
    #: The public unix socket (Caddy upstream). Ignored when serving over TCP (dev).
    socket_path: Path
    #: Group given connect() on the socket (Caddy + the app tier).
    socket_group: str
    #: `host:port` for a dev TCP listener instead of the unix socket ('' = socket).
    tcp_bind: str
    #: Serve /assets and /vendor from the app (dev only; Caddy serves them in prod).
    serve_static: bool
    #: The profile this instance is *born* as (`EULER_PROFILE=%i`). When set,
    #: the app refuses a request whose `X-Profile` differs — the code-side backstop
    #: to Caddy's per-profile routing. Empty (dev) accepts any known profile.
    profile: str
    #: Base URL of the repo on GitHub, for the problem page's source link. It cannot
    #: be derived from `.git/config` — the service uid has no read access to `.git`
    #: — so it is configuration. Empty drops the link rather than guessing.
    github_url: str = 'https://github.com/vikasmunshi/euler'
    #: The branch those source links point at.
    github_branch: str = 'master'

    @classmethod
    def from_env(cls) -> SiteConfig:
        """Build the configuration from the process environment (`[site]` in `env.conf`).

        Two settings are not the table's to give. `repo_root` is *discovered* —
        EULER_REPO_ROOT first (every deployed unit sets it), then
        `solver.config.paths.repo_root`, which refuses to invent a root rather than
        silently adopting site-packages as one — and `static_dir` defaults to a path
        inside whatever tree that turns out to be.
        """
        values = load_spec('site').read(get_type_hints(cls))
        repo_root = find_repo_root()
        config = cls(repo_root=repo_root,
                     static_dir=values.pop('static_dir', repo_root / 'solver/web/content'),
                     **values)
        return config._replace(github_url=config.github_url.rstrip('/'))
