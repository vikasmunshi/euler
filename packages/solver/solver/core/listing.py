#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Which of a problem's files a listing shows — shared by `ls` and the site's files table.

**Config-free and shell-free**, like :mod:`solver.core.progress`: nothing here imports
:mod:`solver.config` or :mod:`solver.shell`, so the web service may import it.
"""
from __future__ import annotations

__all__ = ['HIDDEN_DIRS', 'listable', 'mimetype']

import mimetypes
from pathlib import Path

#: Directories whose contents no listing shows: build droppings, not the problem's files.
HIDDEN_DIRS: frozenset[str] = frozenset({'__pycache__'})


def mimetype(path: Path) -> str | None:
    """The MIME type guessed from *path*'s name, or None when the extension is unknown or absent."""
    return mimetypes.guess_type(path.name)[0]


def listable(path: Path, root: Path) -> bool:
    """Whether a listing of *root* shows the file *path* under it.

    Shown only when its MIME type can be guessed from its name (so files with no extension
    are hidden) and no directory between *root* and it is in :data:`HIDDEN_DIRS`.
    """
    return mimetype(path) is not None and HIDDEN_DIRS.isdisjoint(path.relative_to(root).parts[:-1])
