#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Content-service runtime configuration, read from the environment (DD-5/DD-12).

Like :class:`~solver.web.auth.config.AuthConfig`, every value has an env override
so the service runs unprivileged in a scratch dir for local testing, and it never
touches :mod:`solver.config` (which resolves the shell's identity + repo paths the
service uid cannot use). The deployed unit sets these via ``EnvironmentFile=`` and
one ``EULER_PROFILE=<profile>`` per template-unit instance.
"""
from __future__ import annotations

__all__ = ['SiteConfig']

import os
from pathlib import Path
from typing import NamedTuple

#: Repo root as seen from this file (``solver/web/site/config.py`` → up 3): the
#: default working tree for a dev run straight from a checkout.
_REPO_ROOT = Path(__file__).resolve().parents[3]

#: This repo on GitHub — the default for :attr:`SiteConfig.github_url`, overridable
#: with ``EULER_GITHUB_URL`` (a fork serves its own source links).
_GITHUB_URL = 'https://github.com/vikasmunshi/euler'

#: The branch the source links point at (``EULER_GITHUB_BRANCH``).
_GITHUB_BRANCH = 'master'


def _truthy(value: str) -> bool:
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


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
    #: ``host:port`` for a dev TCP listener instead of the unix socket ('' = socket).
    tcp_bind: str
    #: Serve /assets and /vendor from the app (dev only; Caddy serves them in prod).
    serve_static: bool
    #: The profile this instance is *born* as (``EULER_PROFILE=%i``, DD-12). When set,
    #: the app refuses a request whose ``X-Profile`` differs — the code-side backstop
    #: to Caddy's per-profile routing. Empty (dev) accepts any known profile.
    profile: str
    #: Base URL of the repo on GitHub, for the problem page's source link. It cannot
    #: be derived from ``.git/config`` — the service uid has no read access to ``.git``
    #: (DD-12) — so it is configuration. Empty drops the link rather than guessing.
    github_url: str = _GITHUB_URL
    #: The branch those source links point at.
    github_branch: str = _GITHUB_BRANCH

    @classmethod
    def from_env(cls) -> SiteConfig:
        """Build the configuration from the process environment (all optional)."""
        repo_root = Path(os.environ.get('EULER_REPO_ROOT', str(_REPO_ROOT)))
        static_dir = Path(os.environ.get('EULER_CONTENT_STATIC_DIR',
                                         str(repo_root / 'solver/web/content')))
        return cls(
            repo_root=repo_root,
            static_dir=static_dir,
            socket_path=Path(os.environ.get('EULER_CONTENT_SOCKET', '/run/euler/content.sock')),
            socket_group=os.environ.get('EULER_WEB_GROUP', 'euler-web'),
            tcp_bind=os.environ.get('EULER_CONTENT_TCP', '').strip(),
            serve_static=_truthy(os.environ.get('EULER_CONTENT_SERVE_STATIC', '')),
            profile=os.environ.get('EULER_PROFILE', '').strip(),
            github_url=os.environ.get('EULER_GITHUB_URL', _GITHUB_URL).strip().rstrip('/'),
            github_branch=os.environ.get('EULER_GITHUB_BRANCH', _GITHUB_BRANCH).strip(),
        )
