#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Web shell entry point: `python -m euler_webshell.shell` — what the per-user service's PTY runs."""
from __future__ import annotations

from solver.main import main
from solver.shell.extension import ExtensionError
from euler_webshell.shell import extension

if __name__ == '__main__':  # pragma: no cover — the PTY's process entry
    try:
        ext = extension()
    except ExtensionError as exc:
        raise SystemExit(f'extension: {exc} — refusing to start') from None
    raise SystemExit(main(extension=ext))
