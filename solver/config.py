#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
from __future__ import annotations

from os import chdir
from pathlib import Path
from subprocess import run

from prompt_toolkit.styles import Style
from rich.theme import Theme


def _root_dir() -> Path:
    """Return the git repository root directory, cached after the first lookup."""
    a_package_dir = Path(__file__).parent.resolve()
    result = run('git rev-parse --show-toplevel', capture_output=True, text=True, shell=True,
                 cwd=a_package_dir)
    if result.returncode == 0 and (git_root := result.stdout.strip()) != '':
        chdir(git_root)
        return Path(git_root)
    raise ValueError('Failed to get git root')


class config:
    def __init__(self) -> None:
        raise TypeError('Config is a singleton class')

    root_dir: Path = _root_dir()

    class scripts:
        build_c: str = './scripts/c/build.sh'
        install_chrome: str = './scripts/setup/chrome.sh'
        install_dev_env: str = './scripts/setup/dev_env.sh'
        install_upgrade_service: str = './scripts/setup/upgrade_service.sh'
        publish: str = './scripts/git/publish.sh'
        status: str = './scripts/git/status.sh'
        sync: str = './scripts/git/sync.sh'
        upgrade: str = './scripts/pip/upgrade.sh'
        linter: str = './scripts/linters/check.sh'

    author_email: str = 'vikas.munshi@gmail.com'
    default_results: str = 'Solution pending... the mathematician is still thinking.'
    default_solution_notes: str = 'Nothing here yet - come back when the dust has settled.'
    default_test_cases: str = 'No test cases yet - someone has to go first.'
    keys_version: str = '1.0.1'
    notes_filename: str = 'notes.html'
    number_filename: str = 'problem_number.txt'
    problems_list_url: str = 'https://projecteuler.net/minimal=problems'
    project_git_url: str = 'https://github.com/vikasmunshi/euler'
    projecteuler_url: str = 'https://projecteuler.net'
    resource_dirname: str = 'resources'
    results_filename: str = 'results.json'
    screen_width: int = 86
    statement_filename: str = 'problem.html'
    test_cases_filename: str = 'test_cases.json'
    timeout_multiple: float = 30.0  # timeout in seconds per run when runs > 1
    timeout_single: float = 90.0  # timeout in seconds for single run
    usd_to_eur: float = 0.92  # euros per US dollar, used by `costs`; updated as needed

    aliases_file: Path = root_dir / 'aliases.txt'
    backup_dir: Path = root_dir / '.backup'
    bin_dir: Path = root_dir / '.bin'
    cache_dir: Path = root_dir / '.cache'
    history_file: Path = root_dir / '.history'
    keys_backup_file: Path = root_dir / 'backup/keys_backup.json'
    keys_file: Path = root_dir / 'keys' / 'keys.json'
    private_key_file: Path = Path.home() / '.ssh' / 'id_solver'
    schema_file: Path = root_dir / 'keys' / 'schema.json'
    server_port: int = 8080
    session_file: Path = root_dir / '.session'
    solutions_dir: Path = root_dir / 'solutions'
    solutions_problems_file: Path = solutions_dir / 'problems.json'
    solutions_progress_file: Path = solutions_dir / '.progress.html'
    templates_dir: Path = root_dir / 'solver/templates'
    workspace_dir: Path = root_dir / 'workspace'

    theme = Theme({
        'accent': 'bold #f97316',  # warm orange accent (Junie highlight)
        'accent.dim': '#c2410c',
        'primary': '#e5e7eb',  # near-white body text
        'muted': '#9ca3af',  # secondary / hints
        'success': 'bold #22c55e',
        'warning': 'bold #f59e0b',
        'error': 'bold #ef4444',
        'panel.border': '#3f3f46',
        'prompt.path': '#60a5fa',
        'prompt.symbol': 'bold #f97316',
        'cmd.name': 'bold #fbbf24',
        'cmd.help': '#9ca3af',
    })

    #: prompt-toolkit style for the input line.
    style = Style.from_dict({
        'prompt.bar': '#f97316 bold',
        'prompt.path': '#60a5fa',
        'prompt.symbol': '#f97316 bold',
        'prompt.user': '#e5e7eb',
        '': '#60a5fa',  # typed input text
        'auto-suggestion': '#9ca3af',  # muted light grey
        'bottom-toolbar': 'bg:#27272a #9ca3af',
    })

    modules_with_commands: list[str] = [
        'solver.ai.make',
        'solver.ai.models',
        'solver.core.evaluate',
        'solver.core.workspace',
        'solver.crypto.keys',
        'solver.utils.scripts',
        'solver.utils.solution_files',
        'solver.utils.summary',
        'solver.utils.visualize',
    ]


__all__ = ('config',)
