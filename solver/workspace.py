#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""

"""
from __future__ import annotations

from pathlib import Path

__all__ = [
    'BASE_DIR',
    'MANIFEST_FILENAME',
    'PROBLEMS_LIST_URL',
    'PROJECTEULER_URL',
    'STACK_DIR',
    'WORKSPACE_DIR',
]

# Path constants
BASE_DIR: Path = Path.cwd()  # Project root directory
STACK_DIR: Path = BASE_DIR / 'stack'  # Base stack directory
WORKSPACE_DIR: Path = BASE_DIR / 'workspace'  # Working/temporary files directory
MANIFEST_FILENAME: str = 'manifest.txt'

# URL constants
PROJECTEULER_URL: str = 'https://projecteuler.net'
PROBLEMS_LIST_URL: str = f'{PROJECTEULER_URL}/minimal=problems'
