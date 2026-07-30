#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Shared JSON persistence and untrusted-text hygiene for the service stores.

Every store file lives in its service's private state dir (`/var/lib/euler-auth`,
`/var/lib/euler-msg`), is owned by that service user alone, and is written
atomically at mode `0600` — the service is the sole reader and writer; admin
operations go through the admin API, never through these files.

:func:`sanitize` is here rather than beside any one store because both the stores
that hold **user-authored free text** need it — the invite-request queue
(:mod:`solver.web.auth.requests`) and the message spool
(:mod:`solver.web.msg.store`) — and the second must not import the first
(web-server-guide § Messaging).
"""
from __future__ import annotations

__all__ = ['load_json', 'sanitize', 'save_json']

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
    """Write *data* to *path* atomically (tmp file + rename) at mode `0600`."""
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


def sanitize(text: str, max_len: int, *, allow_newlines: bool = False) -> str:
    """Strip control characters, cap length, and trim — for untrusted free text.

    Drops C0/C1 control characters (so a name, a remark or a message subject cannot
    smuggle newlines into a notification-mail header or control codes into a terminal
    listing); tabs become spaces. With *allow_newlines* the record keeps its line
    breaks (remarks, message bodies), which stay in the mail **body** — or in an
    autoescaped template — where they are inert. The cap is applied last, so the
    stored value never exceeds *max_len*.
    """
    out: list[str] = []
    for ch in text:
        if ch == '\n':
            out.append(ch if allow_newlines else ' ')
        elif ch == '\t':
            out.append(' ')
        elif ch < ' ' or ch == '\x7f' or '\x80' <= ch <= '\x9f':
            continue
        else:
            out.append(ch)
    return ''.join(out).strip()[:max_len]
