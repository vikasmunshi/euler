#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import StrEnum
from os import chdir
from pathlib import Path
from subprocess import run


class ColorCodes(StrEnum):
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ORANGE = '\033[38;5;208m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def __root_dir() -> Path:
    """Return the git repository root directory, cached after the first lookup."""
    a_package_dir = Path(__file__).parent.resolve()
    result = run('git rev-parse --show-toplevel', capture_output=True, text=True, shell=True, cwd=a_package_dir)
    if result.returncode == 0 and (git_root := result.stdout.strip()) != '':
        chdir(git_root)
        return Path(git_root)
    raise ValueError('Failed to get git root')


root_dir: Path = __root_dir()

keys_version: str = '1.0.1'
number_filename: str = 'problem_number.txt'
problems_list_url: str = 'https://projecteuler.net/minimal=problems'
projecteuler_url: str = 'https://projecteuler.net'
resource_dirname: str = 'resources'
results_filename: str = 'results.json'
statement_filename: str = 'problem.html'
test_cases_filename: str = 'test_cases.json'
timeout: float = 300  # timeout in seconds

backup_dir: Path = root_dir / '.backup'
cache_dir: Path = root_dir / '.cache'
history_file: Path = root_dir / '.history'
keys_backup_file: Path = root_dir / 'backup/keys_backup.json'
keys_file: Path = root_dir / 'keys' / 'keys.json'
private_key_file: Path = Path.home() / '.ssh' / 'id_solver'
schema_file: Path = root_dir / 'keys' / 'schema.json'
sessions_dir: Path = root_dir / '.sessions'
solutions_dir: Path = root_dir / 'solutions'
solutions_history_file: Path = solutions_dir / 'history.csv'
workspace_dir: Path = root_dir / 'euler'

__all__ = (
    'ColorCodes',
    'backup_dir',
    'cache_dir',
    'history_file',
    'keys_backup_file',
    'keys_file',
    'keys_version',
    'number_filename',
    'private_key_file',
    'problems_list_url',
    'projecteuler_url',
    'resource_dirname',
    'results_filename',
    'root_dir',
    'schema_file',
    'sessions_dir',
    'solutions_dir',
    'solutions_history_file',
    'statement_filename',
    'test_cases_filename',
    'timeout',
    'workspace_dir',
)
