#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The content service — server-rendered pages + htmx fragments (Phase 5).

An aiohttp + Jinja2 app (autoescape on) that serves the site: home/navigation
(5a), the read-only summary/problem/code/docs views (5b), and the htmx edit
paths (5c/5d). It runs as ``euler-content`` from the ``/opt/euler`` system venv,
one **per-profile instance** behind Caddy (``euler-content@<profile>.service``);
Caddy authenticates every request via ``forward_auth`` and forwards the trusted
``X-User`` / ``X-Profile`` (DD-12), which this app turns into a
:class:`~solver.auth.subject.Subject` to gate its routes.

Import discipline mirrors :mod:`solver.web.auth`: this package imports the
:mod:`solver.auth` kernel but **never** :mod:`solver.config` — under a service
uid the shell's identity resolver would abort. All runtime configuration comes
from the environment (:class:`~solver.web.site.config.SiteConfig`).
"""
from __future__ import annotations

__all__ = ['build_app', 'SiteConfig']

from solver.web.site.app import build_app
from solver.web.site.config import SiteConfig
