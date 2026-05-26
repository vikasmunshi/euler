#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Module entry point."""
from __future__ import annotations

import sys

from solver.main import main

if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
