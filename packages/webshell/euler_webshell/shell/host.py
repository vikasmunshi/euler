#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Host terminal entry point: `python -m euler_webshell.shell.host` — what `solver-host` runs."""
from __future__ import annotations

from euler_webshell.shell import host_main

if __name__ == '__main__':  # pragma: no cover — the process entry
    raise SystemExit(host_main())
