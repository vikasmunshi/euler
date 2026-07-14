#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The per-user web service (MT-4): one collaborator's content **and** web shell.

Replaces the per-*profile* content (:mod:`solver.web.site`) and web-shell
(:mod:`solver.web.ws`) instances with a single per-*user* service: one process per
collaborator, born as their own ``euler-user-<slug>`` uid, reading their own clone
and vault, serving both the content routes and ``/ws`` on one socket that Caddy
dials by ``X-User-Slug`` (MT-7/MT-11). The old per-profile services stay as the
libraries this composes — the content handlers (:mod:`solver.web.site.app`) and the
PTY machinery (:mod:`solver.web.ws`).
"""
from __future__ import annotations

__all__ = ['UserConfig', 'build_app']

from solver.web.user.app import build_app
from solver.web.user.config import UserConfig
