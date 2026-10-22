#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Host terminal entry point: `python -m solver.web.shell.host` — what `solver-host` runs."""
from __future__ import annotations

from solver.web.shell import host_main

if __name__ == '__main__':  # pragma: no cover — the process entry
    raise SystemExit(host_main())
