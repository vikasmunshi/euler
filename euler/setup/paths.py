#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution Info for Project Euler problems."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

MAX_SHARABLE: int = 100


def _get_base_dir(package_name: str | None = None) -> Path:
    package_name = package_name or __package__.split('.')[0]
    _base_dir: Path = Path(__file__).parent
    while _base_dir.name != package_name:
        if _base_dir.parent == _base_dir:  # Check if we’ve reached the root directory
            raise RuntimeError(f'Package root {package_name} not found for the current file: {__file__}')
        _base_dir = _base_dir.parent
    return _base_dir


base_dir: Path = _get_base_dir()


@lru_cache(maxsize=None)
def get_file_path_structure(euler_problem: int, *, sep: Literal['.', '/']) -> str:
    first: int = (100 * ((euler_problem - 1) // 100)) + 1
    last: int = first + 99
    return f'solutions{sep}solutions_{first:04d}_{last:04d}{sep}solution_{euler_problem:04d}'


@lru_cache(maxsize=None)
def get_module_name(euler_problem: int) -> str:
    return 'private' if euler_problem > MAX_SHARABLE else 'solution'


@lru_cache(maxsize=None)
def get_module_path(euler_problem: int) -> Path:
    return base_dir / get_file_path_structure(euler_problem, sep='/') / (get_module_name(euler_problem) + '.py')


@lru_cache(maxsize=None)
def get_answers_path(euler_problem: int) -> Path:
    return base_dir / get_file_path_structure(euler_problem, sep='/') / (get_module_name(euler_problem) + '.json')
