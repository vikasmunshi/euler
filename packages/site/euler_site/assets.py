#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Versioned asset URLs: `/assets/site.css?v=<hash>` — a URL that names its own bytes (shared).

Caddy serves `/assets` and `/vendor` from a copy of this package's `content/` tree. An
unversioned path must be revalidated on every use, because the same path names different
bytes after a redeploy (docs/web-server-guide.md § 11.10). A path that carries a hash of
its file's contents never does: the edge marks a request with `?v=` `immutable` for a
year, and a redeploy that changes the file changes the URL the pages ask for.

The templates write `{{ asset('/assets/site.css') }}`, never the bare path;
`tests/test_assets.py` holds them to it. The hash is read from the installed package — the
same checkout `redeploy-web` copies to the edge, and the copy goes first, so the bytes are
in place before a page names them. A file the package lacks gets its bare path, and with it
the revalidated rule: a missing hash costs a conditional request, never a stale file.

Not covered: what a script imports by itself (site.js's `import('/assets/editor.js')`,
the editor's CodeMirror modules). Those URLs are in the files, not the templates, and keep
the revalidated rule.
"""
from __future__ import annotations

__all__ = ['CONTENT_DIR', 'asset_url', 'install']

import hashlib
from functools import cache
from pathlib import Path

import jinja2

#: The static tree the edge serves, as installed with this package.
CONTENT_DIR: Path = Path(__file__).resolve().parent / 'content'
#: Hex digits of the content hash: enough to tell two builds of one file apart.
_DIGITS: int = 12


@cache
def asset_url(path: str) -> str:
    """*path* (`/assets/…` or `/vendor/…`) with `?v=` its contents' hash, or bare if unreadable.

    Cached for the life of the process: the installed files change only with a redeploy,
    which restarts it.
    """
    try:
        data = (CONTENT_DIR / path.lstrip('/')).read_bytes()
    except OSError:
        return path
    return f'{path}?v={hashlib.sha256(data).hexdigest()[:_DIGITS]}'


def install(env: jinja2.Environment) -> None:
    """Make `asset()` available to every template *env* renders."""
    env.globals['asset'] = asset_url
