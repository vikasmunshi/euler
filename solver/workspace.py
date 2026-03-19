#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Workspace and path configuration for Project Euler solver.

This module defines all directory paths and URL constants used throughout the
Project Euler solver system. It establishes the project structure and provides
centralized configuration for file locations and external resources.

Directory Structure:
    euler/                      # BASE_DIR (project root)
        stack/                  # STACK_DIR (problem cache storage)
            0/0/0/1/           # Problem 1 (hierarchical by digits)
                manifest.txt   # MANIFEST_FILENAME
                problem.html
                problem.md
                ...
            0/1/0/0/           # Problem 100
                manifest.txt
                ...
        workspace/             # WORKSPACE_DIR (active work area)
            number.txt
            title.txt
            problem.md
            resources/
            ...
        keys/
            key.txt            # Encryption key (gitignored)

Module Constants:
    BASE_DIR: Project root directory (current working directory)
    STACK_DIR: Persistent problem storage with hierarchical structure
    WORKSPACE_DIR: Temporary work area for active problem solving
    MANIFEST_FILENAME: Name of manifest files in stack directories
    PROJECTEULER_URL: Base URL for Project Euler website
    PROBLEMS_LIST_URL: URL for minimal problems list

Path Management:
    - All paths are defined as Path objects for cross-platform compatibility
    - Paths are relative to BASE_DIR (project root)
    - Stack uses hierarchical directory structure for organization
    - Workspace is cleared and recreated for each problem

Usage:
    >>> from solver.workspace import WORKSPACE_DIR, STACK_DIR
    >>> problem_file = WORKSPACE_DIR / 'problem.md'
    >>> stack_location = STACK_DIR / '0' / '0' / '0' / '1'

Note:
    - All modules should import paths from this module for consistency
    - Do not hardcode paths elsewhere in the codebase
    - WORKSPACE_DIR is ephemeral and may be cleared at any time
    - STACK_DIR contains persistent cached problem data
"""
from __future__ import annotations

from pathlib import Path
from shutil import rmtree
from typing import Generator

__all__ = [
    'BASE_DIR',
    'MANIFEST_FILENAME',
    'PROBLEMS_LIST_URL',
    'PROJECTEULER_URL',
    'STACK_DIR',
    'WORKSPACE_DIR',
    'clear_workspace',
    'iterdir_recursive',
]

# Path constants
BASE_DIR: Path = Path.cwd()  # Project root directory
STACK_DIR: Path = BASE_DIR / 'stack'  # Base stack directory
WORKSPACE_DIR: Path = BASE_DIR / 'workspace'  # Working/temporary files directory
MANIFEST_FILENAME: str = 'manifest.txt'

# URL constants
PROJECTEULER_URL: str = 'https://projecteuler.net'
PROBLEMS_LIST_URL: str = f'{PROJECTEULER_URL}/minimal=problems'


def clear_workspace() -> None:
    """Clear the workspace directory."""
    rmtree(WORKSPACE_DIR, ignore_errors=True)


def iterdir_recursive(directory: Path) -> Generator[Path, None, None]:
    if not directory.exists():
        return None
    if directory.is_file():
        yield directory
        return None
    for path in directory.iterdir():
        if path.is_dir():
            yield from iterdir_recursive(path)
        elif path.is_file():
            yield path
    return None
