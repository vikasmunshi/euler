#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The static configuration: every path and constant the solver reads, declared once.

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

Where a value comes from
------------------------

Every setting is a field below, with its type and its default. `values.conf` beside this
file may override any of them, and two environment variables outrank both: `EULER_REPO_ROOT`
(via :func:`~solver.config.paths.repo_root`) and `EULER_BASE_URL`. So:

    environment  >  values.conf  >  the default declared here

The defaults are not a formality — they are what makes a missing or mangled values file
survivable rather than fatal. `values.conf` ships stating them, so it is a catalogue of
every knob as well as the place to turn one, and `tests/test_values.py` holds the two
copies to each other.

There is no `config.json` and no `manage-config`. Reading a setting is `{config}` in the
shell (`{config.timeout_single}` for one of them); changing one is editing `values.conf`.
The single value that is *maintained* rather than chosen — `ecb_usd_rate`, refreshed from
the ECB feed by `update-usd-rate` — is written back into that same file, one line at a time.
"""
from __future__ import annotations

__all__ = ['Config', 'ExitCodes', 'Scripts', 'VALUES_FILENAME', 'ValuesError', 'build_config',
           'settable_fields', 'values_file_for']

import enum
import os
from dataclasses import dataclass, field, fields
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, NamedTuple, get_type_hints

from solver.config.paths import package_root, repo_root, secrets_dir
from solver.config.values import ValuesError, coerce, flatten, read_sections

if TYPE_CHECKING:                       # imported lazily by the cached_property that needs it
    from prompt_toolkit.styles import Style
    from rich.theme import Theme

    from solver.auth import Subject

#: The values file's name, looked for beside this module in the working tree first and in
#: the installed package second (they are the same file in a dev checkout).
VALUES_FILENAME: str = 'values.conf'

#: The default for a path that is *derived* from an anchor rather than written out here.
#: `__post_init__` replaces it; a value supplied by `values.conf` is left alone, which is
#: how the file wins without the class having to know whether it was read at all.
_DERIVED: Path = Path('\x00derived')

#: Fields that are not settings, and so are not the values file's to name. The anchors —
#: where the checkout is, where the code was installed — are not matters of opinion, and a
#: file cannot name the file it was itself read from. `scripts` is a setting, but a nested
#: one: it comes from the `[scripts]` section rather than the flat namespace.
_NOT_SETTINGS: frozenset[str] = frozenset({'root_dir', 'package_dir', 'scripts', 'values_file'})


class ExitCodes(enum.IntEnum):
    #: Conventional exit codes, following common shell practice.
    EXIT_OK = 0  #: success
    EXIT_ERROR = 1  #: generic failure
    EXIT_USAGE = 2  #: parse / usage error
    EXIT_ABORT = 3  #: the user declined or quit an interactive dialogue
    EXIT_NOTFOUND = 127  #: unknown command


class Scripts(NamedTuple):
    """The shell scripts the solver drives, as repo-relative command lines.

    Relative on purpose: they are run from the working tree the shell entered at startup
    (:func:`~solver.config.paths.enter_repo`), so they name the same file in a collaborator's
    clone as in the operator's.
    """

    audit: str = './scripts/git/audit.sh'
    compile_c: str = './scripts/c/compile.sh'
    configure_identity: str = './scripts/git/configure-identity.sh'
    install_chrome: str = './scripts/setup/chrome.sh'
    install_dev_env: str = './scripts/setup/dev_env.sh'
    install_upgrade_service: str = './scripts/setup/upgrade_service.sh'
    linter: str = './scripts/linters/check.sh'
    publish: str = './scripts/git/publish.sh'
    status: str = './scripts/git/status.sh'
    sync: str = './scripts/git/sync.sh'
    upgrade: str = './scripts/pip/upgrade.sh'


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


@dataclass
class Config:
    """Every setting, with its type and its default. Build it with :func:`build_config`."""

    #: The running build. Not a setting — no file may claim the code is a version it is not.
    version: ClassVar[str] = _package_version()

    # -- anchors: computed, never read from the values file ------------------------------
    #: The working tree (`EULER_REPO_ROOT`, else discovered — see `paths.repo_root`).
    root_dir: Path = field(default_factory=repo_root)
    #: The installed `solver` package — what ships in the wheel.
    package_dir: Path = package_root

    # -- limits and timeouts -------------------------------------------------------------
    api_timeout: float = 600.0                     #: seconds to wait on one Claude API call
    max_line_length: int = 120                     #: keep in sync with tox.ini [flake8]
    max_output_tokens: int = 10_000                #: ceiling on a generated artifact
    max_retries: int = 3                           #: API/download attempts before giving up
    timeout_multiple: float = 30.0                 #: seconds per run, when runs > 1
    timeout_single: float = 90.0                   #: seconds for a single run

    # -- the names files take inside a problem directory ---------------------------------
    notes_filename: str = 'notes.html'
    resource_dirname: str = 'resources'
    results_filename: str = 'results.json'
    statement_filename: str = 'statement.html'
    tags_filename: str = 'tags.json'
    test_cases_filename: str = 'test_cases.json'

    # -- the outside world ---------------------------------------------------------------
    projecteuler_url: str = 'https://projecteuler.net'
    #: Where `show` / `edit` send a terminal browser. `EULER_BASE_URL` outranks the file.
    base_url: str = 'https://euler.vikasmunshi.com'
    #: Euros per US dollar, for what `costs` reports. Maintained by `update-usd-rate`,
    #: which writes it back into `values.conf` — the one value here that is refreshed
    #: rather than chosen.
    ecb_usd_rate: float = 1.00

    # -- paths derived from the anchors --------------------------------------------------
    backup_dir: Path = _DERIVED
    cache_dir: Path = _DERIVED
    central_tags_file: Path = _DERIVED
    docs_dir: Path = _DERIVED
    #: Project dotenv — API key, SMTP + DNS credentials. Machine-local, in the sibling
    #: secrets dir *outside* the checkout (repo `~/euler` → `~/.euler/env`).
    env_file: Path = _DERIVED
    modules_file: Path = _DERIVED
    solutions_dir: Path = _DERIVED
    #: The X25519 private key that opens everything else (plain PKCS8 PEM, `0600`).
    private_key_file: Path = _DERIVED
    #: This machine's two records: `verify`, and the master key wrapped to this holder.
    enc_key_file: Path = _DERIVED
    #: `{salt, iterations, wrapped_vk}` — the vault key under the password-derived key.
    vault_file: Path = _DERIVED
    #: Rolling backups kept of the private key file.
    private_key_backups: int = 5
    state_dir: Path = _DERIVED
    static_file_problems: Path = _DERIVED
    static_file_progress: Path = _DERIVED
    templates_dir: Path = _DERIVED
    topics_dir: Path = _DERIVED
    topics_index_file: Path = _DERIVED

    # -- the scripts the solver drives ---------------------------------------------------
    scripts: Scripts = Scripts()

    #: The values file this configuration was read from — the one `update-usd-rate` writes.
    #: Not a setting: a file cannot name the file it was read from.
    values_file: Path = _DERIVED

    def __post_init__(self) -> None:
        """Fill in the paths that hang off an anchor, unless the values file set them."""
        secrets: Path = secrets_dir(self.root_dir)
        if self.values_file is _DERIVED:
            self.values_file = values_file_for(self.root_dir)
        for name, derived in (
            ('backup_dir', self.root_dir / '.backup'),
            ('cache_dir', self.root_dir / '.cache'),
            ('central_tags_file', self.root_dir / 'topics' / 'tags.json'),
            ('docs_dir', self.root_dir / 'docs'),
            ('env_file', secrets / 'env'),
            ('modules_file', self.package_dir / 'modules.csv'),
            ('private_key_file', secrets / 'id'),
            ('enc_key_file', secrets / 'enc-key.json'),
            ('vault_file', secrets / 'vault'),
            ('solutions_dir', self.root_dir / 'solutions'),
            ('state_dir', self.root_dir / '.state'),
            ('static_file_problems', self.root_dir / 'solutions' / 'problems.json'),
            ('static_file_progress', self.root_dir / 'solutions' / '.progress.html'),
            ('templates_dir', self.package_dir / 'templates'),
            ('topics_dir', self.root_dir / 'topics'),
            ('topics_index_file', self.root_dir / 'topics' / 'articles.json'),
        ):
            if getattr(self, name) is _DERIVED:
                setattr(self, name, derived)

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

    # -- presentation --------------------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        """Read a setting by name, so `config['key']` and `config.key` agree.

        Both channels resolve the same way — including for the settings that are computed
        rather than stored, which a plain `__dict__` lookup would miss.
        """
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None

    def __str__(self) -> str:
        """Every setting, one per line — what `{config}` renders in the shell.

        This is the whole of what `manage-config` used to show, and it needs no command
        and no privilege to see: it is a variable. Changing one is editing the file named
        on the second line.
        """
        settings: dict[str, Any] = {name: getattr(self, name) for name in settable_fields()}
        settings.update({f'scripts.{name}': value for name, value in self.scripts._asdict().items()})
        width = max(len(name) for name in settings)
        lines = [f'{name:<{width}} : {value}' for name, value in sorted(settings.items())]
        return '\n'.join([f'{"solver":<{width}} : {self.version}',
                          f'{"values_file":<{width}} : {self.values_file}',
                          f'{"root_dir":<{width}} : {self.root_dir}', *lines])


def settable_fields() -> dict[str, type]:
    """The settings `values.conf` may override, mapped to their declared type.

    The anchors are excluded: `root_dir` answers to `EULER_REPO_ROOT` and to where the
    checkout actually is, and `package_dir` to where the code was installed. Neither is a
    matter of opinion, so neither is a knob.
    """
    hints = get_type_hints(Config)
    return {f.name: hints[f.name] for f in fields(Config) if f.name not in _NOT_SETTINGS}


def values_file_for(root: Path) -> Path:
    """Where to read `values.conf` for the checkout at *root* — tree copy, else packaged."""
    tracked: Path = root / 'solver' / 'config' / VALUES_FILENAME
    return tracked if tracked.is_file() else package_root / 'config' / VALUES_FILENAME


def build_config(root: Path | None = None, values_file: Path | None = None) -> Config:
    """Build the configuration: declared defaults, overlaid by `values.conf`, then the env.

    Args:
        root: The working tree. Defaults to :func:`~solver.config.paths.repo_root`.
        values_file: The file to overlay. Defaults to the one for *root*; pass a path that
            does not exist to build the pure defaults (which is how the tests check that
            the shipped file and the declared defaults still say the same thing).

    A value the class does not declare is ignored, and one that will not coerce to its
    declared type leaves the default standing. See :mod:`solver.config.values` for why
    neither is fatal.
    """
    root_dir: Path = root if root is not None else repo_root()
    path: Path = values_file if values_file is not None else values_file_for(root_dir)
    anchors: dict[str, str] = {
        'root_dir': str(root_dir),
        'package_dir': str(package_root),
        'secrets_dir': str(secrets_dir(root_dir)),
        'home_dir': str(Path.home()),
    }
    sections: dict[str, dict[str, str]] = read_sections(path, anchors)
    scripts_raw: dict[str, str] = sections.pop('scripts', {})
    declared: dict[str, type] = settable_fields()
    settings: dict[str, Any] = {}
    for name, raw in flatten(sections, path).items():
        if name not in declared:
            continue                               # a retired setting, or a stray: not fatal
        try:
            settings[name] = coerce(name, raw, declared[name])
        except ValueError:
            continue                               # keep the declared default
    if base_url := os.environ.get('EULER_BASE_URL', '').strip():
        settings['base_url'] = base_url            # the environment outranks the file
    scripts = Scripts(**{name: raw for name, raw in scripts_raw.items()
                         if name in Scripts._fields})
    return Config(root_dir=root_dir, values_file=path, scripts=scripts, **settings)
