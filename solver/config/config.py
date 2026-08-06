#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The static configuration: all paths, constants, command modules and settings.

**Import this module and nothing happens.** It computes paths and holds constants; it does
not chdir, does not rewrite `PATH`, does not resolve an identity and does not import `rich`.
Everything that *does* something is either explicit (:func:`solver.config.paths.enter_repo`,
called by the shell entry point) or lazy (:attr:`Config.subject`, :attr:`Config.theme` —
`cached_property`, resolved on first use, from :mod:`solver.config.identity` and
:mod:`solver.config.theme`).

That purity is the point of the split. The git filter, the five web service tiers and the
test suite all want a path constant or two, and every one of them used to get a relocated
process and a resolved security subject along with it.

Dependencies are therefore stdlib, :mod:`solver.version`, and this package's own helpers —
nothing else at module scope.
"""
from __future__ import annotations

__all__ = ['ExitCodes', 'Config']

import enum
import json
import os
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from solver.config.paths import package_root, repo_root

if TYPE_CHECKING:                       # imported lazily by the cached_property that needs it
    from prompt_toolkit.styles import Style
    from rich.theme import Theme

    from solver.auth import Subject


class ExitCodes(enum.IntEnum):
    #: Conventional exit codes, following common shell practice.
    EXIT_OK = 0  #: success
    EXIT_ERROR = 1  #: generic failure
    EXIT_USAGE = 2  #: parse / usage error
    EXIT_ABORT = 3  #: the user declined or quit an interactive dialogue
    EXIT_NOTFOUND = 127  #: unknown command


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
        """Write a value through to `_data` (so `obj.key = value` updates the record).

        A name declared on the *class* — a `cached_property` such as `subject`, or a
        `ClassVar` — is written as an ordinary instance attribute instead. That is where
        `cached_property` keeps its own cache, so assignment overrides a lazy setting
        rather than being silently swallowed by `_data` and never read again.
        """
        if name == '_data':  # the backing store itself is a genuine instance attribute
            super().__setattr__(name, value)
        elif hasattr(type(self), name):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __getitem__(self, key: str) -> Any:
        """Read a value by name (so `obj['key']` works).

        Item access and attribute access answer the same question, so they resolve the
        same way: `_data` first, then the class — otherwise `config['subject']` would
        `KeyError` on exactly the settings that are resolved rather than stored.
        """
        if key in self._data:
            return self._data[key]
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None


class Scripts(AttributeDict):
    # Annotation-only declarations of the script paths served from `_data` via `__getattr__` (they
    # assign no value, so the lookup falls through to `__getattr__` at runtime). They give static
    # checkers the precise type of each `scripts.<name>` read.
    audit: str
    compile_c: str
    configure_identity: str
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
            'audit': './scripts/git/audit.sh',
            'compile_c': './scripts/c/compile.sh',
            'configure_identity': './scripts/git/configure-identity.sh',
            'install_chrome': './scripts/setup/chrome.sh',
            'install_dev_env': './scripts/setup/dev_env.sh',
            'install_upgrade_service': './scripts/setup/upgrade_service.sh',
            'publish': './scripts/git/publish.sh',
            'status': './scripts/git/status.sh',
            'sync': './scripts/git/sync.sh',
            'upgrade': './scripts/pip/upgrade.sh',
            'linter': './scripts/linters/check.sh',
        })


def _package_version() -> str:
    """The running build's version, read from the tracked `solver/version.py`.

    That module is the single source of truth (written only by
    `scripts/version/release.sh`); importing it needs no git and no install, so this
    is correct everywhere — an editable dev checkout, the detached deployed venv
    (`/opt/euler/venv`), and a bare source tree alike. It equals the wheel
    metadata too: `pyproject.toml` stamps the wheel from the same `__version__`.
    """
    from solver.version import __version__
    return __version__


class Config(AttributeDict):
    version: ClassVar[str] = _package_version()
    #: The subset of settings that `load`/`dump`/`repr` round-trip through `managed_config_file`.
    managed: ClassVar[tuple[str, ...]] = ('timeout_multiple', 'timeout_single', 'ecb_usd_rate')

    # Annotation-only declarations of the settings served from `_data` via `__getattr__` (they assign no
    # value, so the lookup falls through to `__getattr__` at runtime). They give static checkers the
    # precise per-field type of each `config.<name>` read. The dynamic settings below are
    # `cached_property` instead — declared as code, because they are resolved rather than stored.
    root_dir: Path
    package_dir: Path
    managed_config_file: Path
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
    statement_filename: str
    tags_filename: str
    test_cases_filename: str
    timeout_multiple: float
    timeout_single: float
    ecb_usd_rate: float
    backup_dir: Path
    cache_dir: Path
    docs_dir: Path
    env_file: Path
    state_dir: Path
    modules_file: Path
    solutions_dir: Path
    static_file_problems: Path
    static_file_progress: Path
    templates_dir: Path
    topics_dir: Path
    central_tags_file: Path
    topics_index_file: Path

    def __init__(self) -> None:
        package_dir: Path = package_root
        root_dir: Path = repo_root()
        # Project dotenv: API key, SMTP + DNS credentials. Machine-local, in the
        # sibling secrets dir outside the checkout (repo `~/euler` -> `~/.euler/env`).
        env_file: Path = root_dir.parent / f'.{root_dir.name}' / 'env'
        super().__init__(data={
            'root_dir': root_dir,
            'package_dir': package_dir,
            'managed_config_file': root_dir / 'solver/config.json',

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
            'statement_filename': 'statement.html',
            'tags_filename': 'tags.json',
            'test_cases_filename': 'test_cases.json',
            'timeout_multiple': 30.0,  # timeout in seconds per run when runs > 1
            'timeout_single': 90.0,  # timeout in seconds for single run
            'ecb_usd_rate': 1.00,  # euros per US dollar, used by `costs`; updated by update-models cmd

            'backup_dir': root_dir / '.backup',
            'cache_dir': root_dir / '.cache',
            'docs_dir': root_dir / 'docs',
            'env_file': env_file,
            'state_dir': root_dir / '.state',
            'modules_file': package_dir / 'modules.csv',
            'solutions_dir': root_dir / 'solutions',
            'static_file_problems': root_dir / 'solutions/problems.json',
            'static_file_progress': root_dir / 'solutions/.progress.html',
            'templates_dir': package_dir / 'templates',
            'topics_dir': root_dir / 'topics',
            'central_tags_file': root_dir / 'topics' / 'tags.json',
            'topics_index_file': root_dir / 'topics' / 'articles.json',
        })

        self.load_managed_config()

    # -- dynamic settings: resolved on first use, never at import ------------------------

    @cached_property
    def subject(self) -> Subject:
        """The resolved security subject — identity, channel, profile, permissions.

        Lazy because resolving it reaches :mod:`solver.auth` and consumes the web shell's
        one-shot ticket; `solver.main.main` forces it at startup, which is the moment that
        handoff has to happen. See :mod:`solver.config.identity`.
        """
        from solver.config.identity import resolve_identity
        return resolve_identity(self.root_dir)

    @cached_property
    def user_state_dir(self) -> Path:
        """This subject's own state directory (`.state/<slug>`), created on first use."""
        from solver.config.identity import user_state_dir
        return user_state_dir(self.state_dir, self.subject)

    @cached_property
    def history_file(self) -> Path:
        """Per-user shell history, keyed by the resolved identity's slug."""
        return self.user_state_dir / 'history'

    @cached_property
    def last_problem_file(self) -> Path:
        """The per-user record of the last active problem."""
        return self.user_state_dir / 'last_problem'

    @cached_property
    def session_file(self) -> Path:
        """The per-user session capture log (`solver --save`)."""
        return self.user_state_dir / 'session'

    @cached_property
    def theme(self) -> Theme:
        """The `rich` console theme (imports `rich` on first use only)."""
        from solver.config.theme import console_theme
        return console_theme()

    @cached_property
    def style(self) -> Style:
        """The `prompt_toolkit` style for the input line."""
        from solver.config.theme import console_style
        return console_style()

    # -- managed settings ---------------------------------------------------------------

    def __repr__(self) -> str:
        """Return the managed settings as a pretty-printed JSON object."""
        return json.dumps({param: self._data[param] for param in self.managed}, indent=2)

    def dump_managed_config(self) -> None:
        """Persist the managed settings (port, timeouts, FX rate) to `managed_config_file`."""
        self.managed_config_file.write_text(
            json.dumps({param: self._data[param] for param in self.managed}, indent=2))

    def load_managed_config(self) -> None:
        """Overlay the persisted managed settings onto the defaults, ignoring a missing/invalid file.

        Only keys in :data:`managed` are overlaid, and a bad value is skipped rather than
        fatal: the file is data, not code, and must never be able to break startup or reach
        a setting that is not managed. A **retired** setting left behind in an older file
        (or a hand-edited stray) is therefore ignored, not a `KeyError` at import.
        """
        try:
            persisted = json.loads(self.managed_config_file.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return
        for param in self.managed:
            if param not in persisted:
                continue
            try:
                self._data[param] = type(self._data[param])(persisted[param])
            except (TypeError, ValueError):
                continue
