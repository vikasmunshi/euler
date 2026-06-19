#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Singleton Config: all paths, constants, command modules, and managed settings."""
from __future__ import annotations

__all__ = ['ExitCodes', 'Singleton', 'config']

import enum
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, ClassVar, cast

from prompt_toolkit.styles import Style
from rich.theme import Theme


class Singleton(type):
    """Metaclass that caches one instance per class.

    The cache lives on the metaclass and is keyed by the concrete class, so a
    subclass of a singleton is its own, separate singleton.
    """

    _instances: dict[type, object] = {}

    def __call__[T](cls: type[T], *args: Any, **kwargs: Any) -> T:
        instance = Singleton._instances.get(cls)
        if instance is None:
            instance = Singleton._instances[cls] = type.__call__(cls, *args, **kwargs)
        return cast(T, instance)


def _root_dir() -> Path:
    """Return the git repository root directory and set the os env PATH, cached after the first lookup."""
    a_package_dir = Path(__file__).parent.resolve()
    result = subprocess.run('git rev-parse --show-toplevel', capture_output=True, text=True, shell=True,
                            cwd=a_package_dir)
    if result.returncode == 0 and (git_root := result.stdout.strip()) != '':
        os.chdir(git_root)
        env_path: list[str] = [Path(sys.executable).parent.as_posix()] + os.getenv('PATH', '').split(':')
        env_path = [p for p in env_path if not p.startswith('/mnt')]
        env_path = list(dict.fromkeys(env_path))
        os.environ['PATH'] = ':'.join(env_path)
        return Path(git_root)
    raise ValueError('Failed to get git root')


class Scripts(metaclass=Singleton):
    __slots__ = ('compile_c', 'install_chrome', 'install_dev_env', 'install_upgrade_service', 'publish', 'status',
                 'sync', 'upgrade', 'linter',)

    def __init__(self, *,
                 compile_c: str,
                 install_chrome: str,
                 install_dev_env: str,
                 install_upgrade_service: str,
                 publish: str,
                 status: str,
                 sync: str,
                 upgrade: str,
                 linter: str,
                 ) -> None:
        self.compile_c: str = compile_c
        self.install_chrome: str = install_chrome
        self.install_dev_env: str = install_dev_env
        self.install_upgrade_service: str = install_upgrade_service
        self.publish: str = publish
        self.status: str = status
        self.sync: str = sync
        self.upgrade: str = upgrade
        self.linter: str = linter


class Config(metaclass=Singleton):
    __slots__ = ('api_timeout', 'author_email', 'backup_dir', 'bin_dir', 'cache_dir', 'checkout', 'default_results',
                 'default_solution_notes', 'default_test_cases', 'docs_dir', 'ecb_usd_rate', 'history_file',
                 'keys_backup_file', 'keys_file', 'keys_version', 'lock_env_var', 'max_line_length',
                 'max_output_tokens', 'max_retries', 'modules_file', 'notes_filename', 'number_filename',
                 'private_key_file', 'project_git_url', 'projecteuler_url', 'resource_dirname', 'results_filename',
                 'root_dir', 'schema_file', 'screen_width', 'scripts', 'server_lock_file', 'server_port',
                 'session_file', 'skill_dir', 'solutions_dir', 'stale_notes_tolerance_s', 'statement_filename',
                 'static_file_dir', 'static_file_problems', 'static_file_progress', 'static_file_progress_editor',
                 'style', 'templates_dir', 'test_cases_filename', 'theme', 'timeout_multiple', 'timeout_single',
                 'workspace_dir')

    managed_config_file: ClassVar[Path] = Path(__file__).parent / 'config.json'
    version: ClassVar[str] = '0.2'

    def __init__(self, *,
                 scripts: Scripts,

                 backup_dir: str,
                 bin_dir: str,
                 cache_dir: str,
                 checkout: str,
                 docs_dir: str,
                 history_file: str,
                 keys_backup_file: str,
                 keys_file: str,
                 modules_file: str,
                 private_key_file: str,
                 schema_file: str,
                 server_lock_file: str,
                 session_file: str,
                 skill_dir: str,
                 solutions_dir: str,
                 static_file_dir: str,
                 static_file_problems: str,
                 static_file_progress: str,
                 static_file_progress_editor: str,
                 templates_dir: str,
                 workspace_dir: str,

                 theme: Theme,
                 style: Style,
                 ) -> None:
        self.scripts: Scripts = scripts

        self.api_timeout: float = 600.0  # seconds
        self.author_email: str = 'vikas.munshi@gmail.com'
        self.default_results: str = 'Solution pending... the mathematician is still thinking.'
        self.default_solution_notes: str = 'Nothing here yet - come back when the dust has settled.'
        self.default_test_cases: str = 'No test cases yet - someone has to go first.'
        self.keys_version: str = '1.0.1'
        self.lock_env_var: str = 'solver_workspace_lock'
        self.max_line_length: int = 120  # keep in sync with tox.ini [flake8] max-line-length
        self.max_output_tokens: int = 10_000
        self.max_retries: int = 3
        self.notes_filename: str = 'notes.html'
        self.number_filename: str = 'number.txt'
        self.project_git_url: str = 'https://github.com/vikasmunshi/euler'
        self.projecteuler_url: str = 'https://projecteuler.net'
        self.resource_dirname: str = 'resources'
        self.results_filename: str = 'results.json'
        self.screen_width: int = 86
        self.server_port: int = 8080
        self.stale_notes_tolerance_s: float = 2.0  # Seconds a source must out-age notes.html to count notes as stale.
        self.statement_filename: str = 'statement.html'
        self.test_cases_filename: str = 'test_cases.json'
        self.timeout_multiple: float = 30.0  # timeout in seconds per run when runs > 1
        self.timeout_single: float = 90.0  # timeout in seconds for single run
        self.ecb_usd_rate: float = 1.00  # euros per US dollar, used by `costs`; updated by update-models cmd

        root_dir: Path = _root_dir()
        self.root_dir: Path = root_dir
        self.backup_dir: Path = root_dir / backup_dir
        self.bin_dir: Path = root_dir / bin_dir
        self.cache_dir: Path = root_dir / cache_dir
        self.checkout: Path = root_dir / checkout
        self.docs_dir: Path = root_dir / docs_dir
        self.history_file: Path = root_dir / history_file
        self.keys_backup_file: Path = root_dir / keys_backup_file
        self.keys_file: Path = root_dir / keys_file
        self.modules_file: Path = root_dir / modules_file
        self.private_key_file: Path = Path.home() / private_key_file
        self.schema_file: Path = root_dir / schema_file
        self.server_lock_file: Path = root_dir / server_lock_file
        self.session_file: Path = root_dir / session_file
        self.skill_dir: Path = root_dir / skill_dir
        self.solutions_dir: Path = root_dir / solutions_dir
        self.static_file_dir: Path = root_dir / static_file_dir
        self.static_file_problems: Path = root_dir / static_file_problems
        self.static_file_progress: Path = root_dir / static_file_progress
        self.static_file_progress_editor: Path = root_dir / static_file_progress_editor
        self.templates_dir: Path = root_dir / templates_dir
        self.workspace_dir: Path = root_dir / workspace_dir

        self.theme: Theme = theme
        self.style: Style = style

        self.load_managed_config()

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __repr__(self) -> str:
        return json.dumps(
            {'server_port': self.server_port,
             'timeout_multiple': self.timeout_multiple,
             'timeout_single': self.timeout_single,
             'ecb_usd_rate': self.ecb_usd_rate,
             }, indent=2)

    def dump_managed_config(self) -> None:
        self.managed_config_file.write_text(json.dumps(
            {'server_port': self.server_port,
             'timeout_multiple': self.timeout_multiple,
             'timeout_single': self.timeout_single,
             'ecb_usd_rate': self.ecb_usd_rate,
             }, indent=2))

    def load_managed_config(self) -> None:
        try:
            for param, value in json.loads(self.managed_config_file.read_text()).items():
                setattr(self, param, type(self[param])(value))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            pass


config: Config = Config(
    scripts=Scripts(
        compile_c='./scripts/c/compile.sh',
        install_chrome='./scripts/setup/chrome.sh',
        install_dev_env='./scripts/setup/dev_env.sh',
        install_upgrade_service='./scripts/setup/upgrade_service.sh',
        publish='./scripts/git/publish.sh',
        status='./scripts/git/status.sh',
        sync='./scripts/git/sync.sh',
        upgrade='./scripts/pip/upgrade.sh',
        linter='./scripts/linters/check.sh',
    ),

    backup_dir='.backup',
    bin_dir='.bin',
    cache_dir='.cache',
    checkout='.checkout',
    docs_dir='docs',
    history_file='.history',
    keys_backup_file='backup/keys_backup.json',
    keys_file='keys/keys.json',
    modules_file='solver/modules.csv',
    private_key_file='.ssh/id_solver',
    schema_file='keys/schema.json',
    server_lock_file='.server.lock',
    session_file='.session',
    skill_dir='solver/ai/claude/skills/claude-euler-solver',
    solutions_dir='solutions',
    static_file_dir='solutions/static-content',
    static_file_problems='solutions/static-content/problems.json',
    static_file_progress='solutions/.progress.html',
    static_file_progress_editor='solutions/static-content/progress-editor.html',
    templates_dir='solver/templates',
    workspace_dir='workspace',

    theme=Theme({
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
        # Markdown rendering (rich.markdown.Markdown) — keyed only by rich's Markdown
        # renderer; tuned to the dark theme so inline code etc. stay readable (no bg block).
        'markdown.code': 'bold #fbbf24',  # inline `code` — amber, no background
        'markdown.code_block': '#fbbf24',
        'markdown.item.bullet': 'bold #f97316',
        'markdown.h1': 'bold #f97316',
        'markdown.h2': 'bold #f97316',
        'markdown.h3': 'bold #fbbf24',
        'markdown.h4': 'bold #fbbf24',
        'markdown.link': '#60a5fa',
        'markdown.link_url': '#60a5fa',
    }),
    #: prompt-toolkit style for the input line.
    style=Style.from_dict({
        'prompt.bar': '#f97316 bold',
        'prompt.path': '#60a5fa',
        'prompt.path.unlocked': '#475569',  # dimmed: workspace lock not held
        'prompt.symbol': '#f97316 bold',
        'prompt.user': '#e5e7eb',
        '': '#60a5fa',  # typed input text
        'auto-suggestion': '#9ca3af',  # muted light grey
        'bottom-toolbar': 'bg:#27272a #9ca3af',
    }),
)


class ExitCodes(enum.IntEnum):
    #: Conventional exit codes, following common shell practice.
    EXIT_OK = 0  #: success
    EXIT_ERROR = 1  #: generic failure
    EXIT_USAGE = 2  #: parse / usage error
    EXIT_NOTFOUND = 127  #: unknown command
