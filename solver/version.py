#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The solver build version — the single source of truth.

This file is the *one* place the version number lives. It is rewritten **only**
by ``scripts/version/release.sh``, which bumps this number and creates the matching
``vX.Y.Z`` git tag in one release step — never hand-edit it. ``pyproject.toml``
reads ``__version__`` from here at build time (setuptools ``attr:``) to stamp the
wheel, and ``solver.config`` imports it for the running build's version, so the
number in the tag, the wheel metadata, and the shell always agree.

It holds the last *released* number; between releases it stays put while the
`version` command's live ``git describe`` line shows how far past the tag HEAD is.
"""
from __future__ import annotations

__all__ = ['__version__', 'version']

__version__ = '0.8.0'
version = __version__
