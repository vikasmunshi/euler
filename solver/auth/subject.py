#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The authorization **subject** — the resolved security principal (DD-12).

One immutable value describing *who* is running this process and *what* they may
do, resolved once at startup by :func:`solver.auth.identity.resolve_subject`.
Every enforcement point (the command decorator, the web app router) checks
against it; nothing else re-derives identity.
"""
from __future__ import annotations

__all__ = ['Subject']

from typing import NamedTuple


class Subject(NamedTuple):
    """The resolved principal: identity, channel, and expanded permissions.

    - ``user``        — the raw identity (email for web, OS login for terminal),
                        for prompts/logs and per-user state.
    - ``slug``        — filesystem-safe form of ``user`` (per-user state dirs).
    - ``channel``     — ``'terminal'`` or ``'web'``: where this process runs.
    - ``auth_method`` — how identity was proven (``shell-ticket`` / ``os-login``
                        / ``checkout-owner``), for audit.
    - ``profile``     — the assigned role (``reader``/``contributor``/
                        ``maintainer``/``admin``).
    - ``permissions`` — the inheritance-expanded ``object:permission`` grant set.
    """

    user: str
    slug: str
    channel: str
    auth_method: str
    profile: str
    permissions: frozenset[str]

    def has(self, permission: str) -> bool:
        """True if this subject holds *permission* (an ``object:permission`` string)."""
        return permission in self.permissions

    def has_all(self, permissions: tuple[str, ...]) -> bool:
        """True if this subject holds **every** permission in *permissions* (fail-closed on empty-grant)."""
        return self.permissions.issuperset(permissions)
