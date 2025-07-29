#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base directory for the project."""
from __future__ import annotations

from pathlib import Path

__all__ = ['base_dir']


def _get_base_dir(package_name: str | None = None) -> Path:
    package_name = package_name or __package__.split('.')[0]
    _base_dir: Path = Path(__file__).parent
    while _base_dir.name != package_name:
        if _base_dir.parent == _base_dir:  # Check if we’ve reached the root directory
            raise RuntimeError(f'Package root {package_name} not found for the current file: {__file__}')
        _base_dir = _base_dir.parent
    return _base_dir


base_dir: Path = _get_base_dir()
