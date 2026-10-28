#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The euler-site build version — in lockstep with `solver.version` (docs/package-guide.md § 5.2).

Rewritten **only** by `scripts/version/release.sh`, together with every other package's
version.py and the pins between them — never hand-edit it.
"""
from __future__ import annotations

__all__ = ['__version__', 'version']

__version__ = '4.19.0'
version = __version__
