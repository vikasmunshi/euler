#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Shared JSON persistence for the auth stores.

Every store file lives in the service's private state dir
(``/var/lib/euler-auth``), is owned by ``euler-auth`` alone, and is written
atomically at mode ``0600`` — the service is the sole reader and writer; admin
operations go through the admin API, never through these files.
"""
from __future__ import annotations

__all__ = ['load_json', 'save_json']

import json
import os
import tempfile
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    """Return the JSON object at *path*; an empty dict if absent or invalid."""
    try:
        data: Any = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Write *data* to *path* atomically (tmp file + rename) at mode ``0600``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f'.{path.name}.')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write('\n')
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
    except BaseException:
        os.unlink(tmp_name)
        raise
