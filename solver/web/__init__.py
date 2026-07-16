#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The web app services (see docs/web-server-guide.md).

Each sub-package is one isolated service: it listens on a unix domain socket
under ``/run/euler/``, runs as its own dedicated system user from the
``/opt/euler`` system venv, and is reached only through the Caddy edge (or, for
admin planes, a group-gated local socket).

Hard rule: nothing under ``solver.web`` may import :mod:`solver.config` — the
service users cannot read the repo checkout, and config construction resolves
the *shell's* identity, which a service must not do. Each service reads its own
scoped environment (e.g. ``/etc/euler/auth.env``) instead.
"""
