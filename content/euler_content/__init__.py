#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The published content, packaged: what the public site serves to visitors who are not signed in.

`tree/` mirrors the repository's own layout for the public paths — `README.md`, `docs/`,
`topics/`, `solutions/public/`, `solutions/problems.json`, and the few `solver/` files the
pages link to — so the site reads it exactly as it reads a clone. It holds no
`solutions/private`: the private solutions are not in this package at all
(`scripts/content/stage.py` builds it from tracked files and refuses one).
"""
from __future__ import annotations

__all__ = ['root']

from importlib.resources import as_file, files
from pathlib import Path


def root() -> Path:
    """The installed content tree (a real directory: the wheel installs unzipped)."""
    with as_file(files(__name__) / 'tree') as path:
        return Path(path)
