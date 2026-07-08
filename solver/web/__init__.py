#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web app services (server redesign, docs/server-redesign.md).

Each sub-package is one isolated service (DD-1/DD-2): it listens on a unix
domain socket under ``/run/euler/``, runs as its own dedicated system user from
the ``/opt/euler`` system venv (DD-5), and is reached only through the Caddy
edge (or, for admin planes, a group-gated local socket).

Hard rule: nothing under ``solver.web`` may import :mod:`solver.config` — the
service users cannot read the repo checkout, and config construction resolves
the *shell's* identity (DD-9), which a service must not do. Each service reads
its own scoped environment (e.g. ``/etc/euler/auth.env``) instead.
"""
