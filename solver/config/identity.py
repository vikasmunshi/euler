#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Dynamic configuration: **who** this process is running as.

The static half of the configuration is a function of the checkout — the same values
in every process that reads the same tree. This half is not: it is resolved once per
process from the ambient identity, and it decides what the shell may do and where its
state lives. It is kept out of :mod:`solver.config.settings` for that reason, and because
resolving it costs an import of :mod:`solver.auth` that the git-filter path must not pay.

Resolution is deliberately *lazy* — :attr:`solver.config.Config.subject` is a
`cached_property`, so it happens on first use rather than at import. :func:`solver.main.main`
settles it at startup through :mod:`solver.shell.login`, before any command module loads.
"""
from __future__ import annotations

__all__ = ['resolve_identity', 'user_state_dir']

from pathlib import Path

from solver.auth import Subject, resolve_subject


def resolve_identity(root: Path) -> Subject:
    """Resolve the security subject for this process: the OS login and its role.

    A front end that brings its own identity (the web shell's one-time ticket) sets
    `config.subject` before anything reads it (:mod:`solver.shell.login`), so this default
    is never reached there.
    """
    return resolve_subject(root)


def user_state_dir(state_dir: Path, subject: Subject) -> Path:
    """This subject's own state directory (`.state/<slug>`), created if absent.

    Per-user shell state — history, session log, last active problem — is keyed by the
    resolved slug, so two collaborators sharing a host never share a history file.
    """
    path: Path = state_dir / subject.slug
    path.mkdir(parents=True, exist_ok=True)
    return path
