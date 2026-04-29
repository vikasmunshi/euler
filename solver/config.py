#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import StrEnum
from os import chdir
from pathlib import Path
from subprocess import run


def _root_dir() -> Path:
    """Return the git repository root directory, cached after the first lookup."""
    a_package_dir = Path(__file__).parent.resolve()
    result = run('git rev-parse --show-toplevel', capture_output=True, text=True, shell=True, cwd=a_package_dir)
    if result.returncode == 0 and (git_root := result.stdout.strip()) != '':
        chdir(git_root)
        return Path(git_root)
    raise ValueError('Failed to get git root')


root_dir: Path = _root_dir()

backup_dirname: str = 'backup'
problem_number_filename: str = 'problem_number.txt'
problem_statement_filename: str = 'problem.html'
problems_list_url: str = 'https://projecteuler.net/minimal=problems'
projecteuler_url: str = 'https://projecteuler.net'
resource_dirname: str = 'resources'
test_cases_filename: str = 'test_cases.json'
timeout: float = 300  # timeout in seconds

cache_dir: Path = root_dir / 'cache'
keys_backup_file: Path = root_dir / 'backup/keys_backup.json'
private_key_file: Path = Path.home() / '.ssh' / 'id_solver'
workspace_dir: Path = root_dir / 'euler'  # Working/temporary files directory
problem_number_file: Path = workspace_dir / problem_number_filename
results_file: Path = workspace_dir / 'results.txt'
stack_dir: Path = root_dir / 'stack'

keys_file: Path = root_dir / 'keys' / 'keys.json'
keys_version: str = '1.0.1'
schema_file: Path = root_dir / 'keys' / 'schema.json'
upload_keys_to_origin: Path = root_dir / 'scripts' / 'upload_keys_to_origin.sh'


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
