#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Singleton Config: all paths, constants, command modules, and managed settings."""
from __future__ import annotations

__all__ = ['ExitCodes', 'config']

import enum
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, ClassVar

from prompt_toolkit.styles import Style
from rich.theme import Theme

from solver.utils.identity import resolve_identity


class ExitCodes(enum.IntEnum):
    #: Conventional exit codes, following common shell practice.
    EXIT_OK = 0  #: success
    EXIT_ERROR = 1  #: generic failure
    EXIT_USAGE = 2  #: parse / usage error
    EXIT_NOTFOUND = 127  #: unknown command


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


class AttributeDict:
    """A dict-like object that exposes its keys as attributes."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data: dict[str, Any] = data

    def __getattr__(self, name: str) -> Any:
        """Read a value as an attribute (so `obj.key` works), backed by `_data`."""
        if name == '_data':  # guard the backing store itself against recursion before __init__ sets it
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: Any) -> None:
        """Write a value through to `_data` (so `obj.key = value` updates the record)."""
        if name == '_data':  # the backing store itself is a genuine instance attribute
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __getitem__(self, key: str) -> Any:
        """Read a value by name (so `obj['key']` works)."""
        return self._data[key]


class Scripts(AttributeDict):
    # Annotation-only declarations of the script paths served from `_data` via `__getattr__` (they
    # assign no value, so the lookup falls through to `__getattr__` at runtime). They give static
    # checkers the precise type of each `scripts.<name>` read.
    compile_c: str
    install_chrome: str
    install_dev_env: str
    install_upgrade_service: str
    publish: str
    status: str
    sync: str
    upgrade: str
    linter: str

    def __init__(self) -> None:
        super().__init__(data={
            'compile_c': './scripts/c/compile.sh',
            'install_chrome': './scripts/setup/chrome.sh',
            'install_dev_env': './scripts/setup/dev_env.sh',
            'install_upgrade_service': './scripts/setup/upgrade_service.sh',
            'publish': './scripts/git/publish.sh',
            'status': './scripts/git/status.sh',
            'sync': './scripts/git/sync.sh',
            'upgrade': './scripts/pip/upgrade.sh',
            'linter': './scripts/linters/check.sh',
        })


class Config(AttributeDict):
    managed_config_file: ClassVar[Path] = Path(__file__).parent / 'config.json'
    version: ClassVar[str] = '0.2'
    #: The subset of settings that `load`/`dump`/`repr` round-trip through `managed_config_file`.
    managed: ClassVar[tuple[str, ...]] = ('server_port', 'timeout_multiple', 'timeout_single', 'ecb_usd_rate')

    # Annotation-only declarations of the settings served from `_data` via `__getattr__` (they assign no
    # value, so the lookup falls through to `__getattr__` at runtime). They give static checkers the
    # precise per-field type of each `config.<name>` read.
    scripts: Scripts
    api_timeout: float
    max_line_length: int
    max_output_tokens: int
    max_retries: int
    notes_filename: str
    projecteuler_url: str
    base_url: str
    resource_dirname: str
    results_filename: str
    screen_width: int
    server_port: int
    statement_filename: str
    test_cases_filename: str
    timeout_multiple: float
    timeout_single: float
    ecb_usd_rate: float
    user: str
    user_slug: str
    user_profile: str
    root_dir: Path
    backup_dir: Path
    cache_dir: Path
    docs_dir: Path
    env_file: Path
    state_dir: Path
    user_state_dir: Path
    history_file: Path
    last_problem_file: Path
    modules_file: Path
    commands_file: Path
    server_lock_file: Path
    session_file: Path
    solutions_dir: Path
    users_file: Path
    pending_file: Path
    remember_file: Path
    session_secret_file: Path
    static_file_dir: Path
    static_file_problems: Path
    static_file_progress: Path
    templates_dir: Path
    theme: Theme
    style: Style

    def __init__(self) -> None:
        root_dir: Path = _root_dir()
        # Ambient per-user identity (SOLVER_USER / keys/.env / keys/.user-email / OS login),
        # used to key per-user shell state (history, last problem). Personalisation
        # only — not a security boundary (see solver.utils.identity).
        env_file: Path = root_dir / 'keys' / '.env'  # project dotenv: API key, SMTP + DNS credentials
        users_file: Path = root_dir / 'keys' / '.users.json'  # web-auth SRP verifiers (separate from crypto keys)
        user, user_slug, user_profile = resolve_identity(root_dir, users_file, env_file)
        user_state_dir: Path = root_dir / '.state' / user_slug
        user_state_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(data={
            'scripts': Scripts(),

            'api_timeout': 600.0,  # seconds
            'max_line_length': 120,  # keep in sync with tox.ini [flake8] max-line-length
            'max_output_tokens': 10_000,
            'max_retries': 3,
            'notes_filename': 'notes.html',
            'projecteuler_url': 'https://projecteuler.net',
            'base_url': os.environ.get('EULER_BASE_URL', 'https://euler.vikasmunshi.com'),
            'resource_dirname': 'resources',
            'results_filename': 'results.json',
            'screen_width': 86,
            'server_port': 8080,
            'statement_filename': 'statement.html',
            'test_cases_filename': 'test_cases.json',
            'timeout_multiple': 30.0,  # timeout in seconds per run when runs > 1
            'timeout_single': 90.0,  # timeout in seconds for single run
            'ecb_usd_rate': 1.00,  # euros per US dollar, used by `costs`; updated by update-models cmd

            'user': user,
            'user_slug': user_slug,
            'user_profile': user_profile,
            'root_dir': root_dir,
            'backup_dir': root_dir / '.backup',
            'cache_dir': root_dir / '.cache',
            'docs_dir': root_dir / 'docs',
            'env_file': env_file,
            'state_dir': root_dir / '.state',
            'user_state_dir': user_state_dir,
            # Per-user shell state, keyed by the resolved identity's slug.
            'history_file': user_state_dir / 'history',
            'last_problem_file': user_state_dir / 'last_problem',
            'modules_file': root_dir / 'solver/modules.csv',
            'commands_file': root_dir / 'solver/commands.csv',  # per-profile command authorization policy
            'server_lock_file': root_dir / '.server.lock',
            'session_file': user_state_dir / 'session',
            'solutions_dir': root_dir / 'solutions',
            'users_file': users_file,
            'pending_file': root_dir / 'keys' / '.pending.json',  # invite/reset link tokens, shared shell<->server
            'remember_file': root_dir / 'keys' / '.remember.json',  # persistent remember-me tokens
            'session_secret_file': root_dir / 'keys' / '.session-secret',  # HMAC key for remember-me
            'static_file_dir': root_dir / 'solver/web-content',
            'static_file_problems': root_dir / 'solutions/problems.json',
            'static_file_progress': root_dir / 'solutions/.progress.html',
            'templates_dir': root_dir / 'solver/templates',

            'theme': Theme({
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
            'style': Style.from_dict({
                'prompt.bar': '#f97316 bold',
                'prompt.path': '#60a5fa',
                'prompt.symbol': '#f97316 bold',
                'prompt.user': '#e5e7eb',
                '': '#60a5fa',  # typed input text
                'auto-suggestion': '#9ca3af',  # muted light grey
                'bottom-toolbar': 'bg:#27272a #9ca3af',
            }),
        })

        self.load_managed_config()

    def __repr__(self) -> str:
        """Return the managed settings as a pretty-printed JSON object."""
        return json.dumps({param: self._data[param] for param in self.managed}, indent=2)

    def dump_managed_config(self) -> None:
        """Persist the managed settings (port, timeouts, FX rate) to `managed_config_file`."""
        self.managed_config_file.write_text(
            json.dumps({param: self._data[param] for param in self.managed}, indent=2))

    def load_managed_config(self) -> None:
        """Overlay any persisted managed settings onto the defaults, ignoring a missing/invalid file."""
        try:
            for param, value in json.loads(self.managed_config_file.read_text()).items():
                self._data[param] = type(self._data[param])(value)
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            pass


config: Config = Config()
