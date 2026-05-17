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
    result = run('git rev-parse --show-toplevel', capture_output=True, text=True, shell=True,
                 cwd=a_package_dir)
    if result.returncode == 0 and (git_root := result.stdout.strip()) != '':
        chdir(git_root)
        return Path(git_root)
    raise ValueError('Failed to get git root')


class Config:
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

    class ScriptPaths(StrEnum):
        BUILD_C = './scripts/c/build.sh'
        INSTALL_CHROME = './scripts/setup/chrome.sh'
        INSTALL_DEV_ENV = './scripts/setup/dev_env.sh'
        INSTALL_UPGRADE_SERVICE = './scripts/setup/upgrade_service.sh'
        PUBLISH = './scripts/git/publish.sh'
        STATUS = './scripts/git/status.sh'
        SYNC = './scripts/git/sync.sh'
        UPGRADE = './scripts/pip/upgrade.sh'

    root_dir: Path = _root_dir()

    default_results: str = 'Solution pending... the mathematician is still thinking.'
    default_solution_notes: str = 'Nothing here yet - come back when the dust has settled.'
    default_test_cases: str = 'No test cases yet - someone has to go first.'
    keys_version: str = '1.0.1'
    number_filename: str = 'problem_number.txt'
    problems_list_url: str = 'https://projecteuler.net/minimal=problems'
    project_git_url: str = 'https://github.com/vikasmunshi/euler'
    projecteuler_url: str = 'https://projecteuler.net'
    resource_dirname: str = 'resources'
    results_filename: str = 'results.json'
    screen_width: int = 86
    statement_filename: str = 'problem.html'
    test_cases_filename: str = 'test_cases.json'
    timeout_multiple: float = 5.0  # timeout in seconds per run when runs > 1
    timeout_single: float = 60.0  # timeout in seconds for single run

    aliases_file: Path = root_dir / 'aliases.txt'
    backup_dir: Path = root_dir / '.backup'
    bin_dir: Path = root_dir / '.bin'
    cache_dir: Path = root_dir / '.cache'
    history_file: Path = root_dir / '.history'
    keys_backup_file: Path = root_dir / 'backup/keys_backup.json'
    keys_file: Path = root_dir / 'keys' / 'keys.json'
    private_key_file: Path = Path.home() / '.ssh' / 'id_solver'
    schema_file: Path = root_dir / 'keys' / 'schema.json'
    sessions_dir: Path = root_dir / '.sessions'
    solutions_dir: Path = root_dir / 'solutions'
    solutions_progress_file: Path = solutions_dir / '.progress.html'
    solutions_summary_file: Path = solutions_dir / 'index.html'
    templates_dir: Path = root_dir / 'solver/templates'
    workspace_dir: Path = root_dir / 'workspace'

    def __init__(self) -> None:
        raise TypeError('Config is a singleton class')


__all__ = ('Config',)

if __name__ == '__main__':
    print(Config.root_dir)
