#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Dynamic configuration: **who** this process is running as.

The static half of the configuration is a function of the checkout — the same values
in every process that reads the same tree. This half is not: it is resolved once per
process from the ambient identity, and it decides what the shell may do and where its
state lives. It is kept out of :mod:`solver.config.config` for that reason, and because
resolving it costs an import of :mod:`solver.auth` that the git-filter path must not pay.

Resolution is deliberately *lazy* — :attr:`solver.config.Config.subject` is a
`cached_property`, so it happens on first use rather than at import. :func:`solver.main.main`
forces it at startup, which is where the one-shot ticket handoff below needs to happen while
there is still exactly one process holding it.
"""
from __future__ import annotations

__all__ = ['resolve_identity', 'user_state_dir']

import os
from pathlib import Path

from solver.auth import INSTANCE_EMAIL_ENV, Subject, TICKET_ENV, resolve_subject


def resolve_identity(root: Path) -> Subject:
    """Resolve the security subject for this process, and hand identity down to children.

    Ambient identity + profile: a one-time shell ticket (web PTY) or the checkout-owner
    uid (local terminal); anything else aborts. The subject is identity + channel +
    profile + inheritance-expanded permissions, from `authorizations.json` (deployed SoR →
    built-in default), and it drives per-user state and command/route authorization.

    The handoff is the second half. The web shell's ticket is single-use and
    `resolve_subject` just consumed it; it is scrubbed so a child solver (`claude-solve`'s
    headless Claude, a nested `solver "…"`) does not inherit a dead ticket and abort at its
    own startup. The resolved e-mail goes down in its place: under this per-user uid the
    child re-resolves via the instance-identity plane, which trusts the e-mail only because
    `system_slug(email)` matches the uid's `EULER_USER_SLUG` pin — an env value a child
    cannot forge past. Terminal subjects carry neither var.
    """
    subject: Subject = resolve_subject(root)
    if subject.channel == 'web':
        os.environ.pop(TICKET_ENV, None)
        os.environ[INSTANCE_EMAIL_ENV] = subject.user
    return subject


def user_state_dir(state_dir: Path, subject: Subject) -> Path:
    """This subject's own state directory (`.state/<slug>`), created if absent.

    Per-user shell state — history, session log, last active problem — is keyed by the
    resolved slug, so two collaborators sharing a host never share a history file.
    """
    path: Path = state_dir / subject.slug
    path.mkdir(parents=True, exist_ok=True)
    return path
