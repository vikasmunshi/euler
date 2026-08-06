#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Reading `env.conf` — which environment variable carries each web-service setting.

The web services are configured by their environment rather than by `values.conf`: each
runs as its own uid, from `/opt/euler`, with a scoped `EnvironmentFile=` under `/etc/euler`.
What used to be spread across five `from_env` methods — the variable's name, its default,
and the coercion — is one table here, so `EULER_WEB_GROUP`'s default is stated once instead
of five times and every variable the deployment sets is visible in one place.

**Importing this module must not construct a `Config`.** Three of the services have no
working tree and no `EULER_REPO_ROOT`, so `repo_root()` raises for them by design; that is
why :mod:`solver.config` resolves its singleton lazily, and why nothing here reaches for it.
Stdlib-only, and no side effects at import.

What stays in the calling class, because it is behaviour rather than data: normalising a
value (lowercasing an address, stripping a trailing slash), computing one from another (a
socket path that embeds the instance's slug), and anything with no variable behind it at
all.
"""
from __future__ import annotations

__all__ = ['REQUIRED', 'EnvSpec', 'MissingSetting', 'load_spec']

import os
from configparser import ConfigParser, Error as ConfigParserError
from pathlib import Path
from typing import Any, NamedTuple

from solver.config.paths import package_root
from solver.config.values import coerce

#: The default that means "there is none": the service refuses to start without it.
REQUIRED: str = '!required'

#: Section holding the settings several services share, so their defaults are stated once.
COMMON_SECTION: str = 'common'

#: The file, beside this module. Read from the installed package: unlike `values.conf`,
#: which a collaborator edits in their clone, this is a map of deployment wiring that
#: changes only when the code does — and the services that read it have no clone at all.
ENV_FILE: Path = package_root / 'config' / 'env.conf'


class MissingSetting(SystemExit):
    """A required setting has no value. A `SystemExit`, because that is what it must cause.

    Raised at startup, naming the variable, rather than letting the service run on a guess:
    a wrong `EULER_BASE_URL` mails invite links that go nowhere, and an empty admin token
    would leave the admin plane's second factor as the empty string.
    """


class Entry(NamedTuple):
    """One line of the table: where a setting's value comes from, and what it is without one."""

    env_var: str
    default: str

    @property
    def required(self) -> bool:
        return self.default == REQUIRED


class EnvSpec(NamedTuple):
    """One service's settings, resolved against the process environment on demand."""

    service: str
    entries: dict[str, Entry]

    def raw(self, field: str) -> str:
        """The value for *field* as text: the environment, else the declared default."""
        entry = self.entries[field]
        value: str = os.environ.get(entry.env_var, '')
        if value:
            return value
        if entry.required:
            raise MissingSetting(f'{self.service} service: {entry.env_var} must be set')
        return entry.default

    def get(self, field: str, declared: type) -> Any:
        """The value for *field*, coerced to *declared*.

        A value that will not coerce is a stated intention that cannot be honoured — unlike
        `values.conf`, where a default stands ready to be fallen back on — so it is a
        startup failure naming the variable.
        """
        raw = self.raw(field)
        try:
            return coerce(field, raw, declared)
        except ValueError as exc:
            raise MissingSetting(
                f'{self.service} service: {self.entries[field].env_var}={raw!r} is not a '
                f'valid {declared.__name__} ({exc})') from None

    def read(self, declared: dict[str, type]) -> dict[str, Any]:
        """Every field in *declared* that the table names, coerced — ready to splat into the class.

        A field whose value comes out empty is **omitted** when its type cannot represent
        emptiness — a `Path`, an `int`, a `float` — leaving the class to supply it, because
        `Path('')` is the current directory and `int('')` is an error, and neither is what
        an unset variable meant. For a `str` and a `bool` the empty value is the answer: an
        unset `EULER_PROFILE` is "any profile", an unset `EULER_CONTENT_SERVE_STATIC` is
        "no". Those two distinctions are the whole of what this rule exists for.
        """
        values: dict[str, Any] = {}
        for field, hint in declared.items():
            if field not in self.entries:
                continue
            if not self.raw(field) and hint in (Path, int, float):
                continue
            values[field] = self.get(field, hint)
        return values


def _parse(text: str, path: Path) -> dict[str, dict[str, Entry]]:
    """Split each `<field> = <ENV_VAR> | <default>` line into its two halves."""
    parser = ConfigParser(interpolation=None, comment_prefixes=('#',))
    parser.optionxform = str  # type: ignore[method-assign,assignment]  # field names, verbatim
    parser.read_string(text, source=str(path))
    table: dict[str, dict[str, Entry]] = {}
    for section in parser.sections():
        entries: dict[str, Entry] = {}
        for field, raw in parser.items(section):
            env_var, separator, default = raw.partition('|')
            if not separator:
                raise ValueError(f'{path}: [{section}] {field}: expected `ENV_VAR | default`')
            entries[field] = Entry(env_var=env_var.strip(), default=default.strip())
        table[section] = entries
    return table


def load_spec(service: str, path: Path = ENV_FILE) -> EnvSpec:
    """The spec for *service*: its own section, laid over the shared `[common]` one.

    A service that names a field `[common]` also names — `auth`'s `socket_path`, say —
    takes its own entry, so sharing a default never costs the ability to differ from it.

    Raises:
        ValueError: if the file is missing, malformed, or names no such service. Unlike
            `values.conf` this is not user data with a default behind it; it ships with
            the code, and if it cannot be read the service has no configuration at all.
    """
    try:
        table = _parse(path.read_text(encoding='utf-8'), path)
    except (ConfigParserError, OSError, UnicodeDecodeError) as exc:
        raise ValueError(f'cannot read the environment table at {path}: {exc}') from None
    if service not in table:
        raise ValueError(f'{path}: no [{service}] section')
    return EnvSpec(service=service, entries={**table.get(COMMON_SECTION, {}), **table[service]})
