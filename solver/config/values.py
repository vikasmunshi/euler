#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Reading `values.conf` — the editable half of the configuration.

The settings themselves are declared, typed and defaulted in :mod:`solver.config.config`.
This module only turns the text file beside it into `{name: value}`, coerced to those
declared types. Nothing here decides *what* a setting is; a key the class does not declare
is ignored, and a value that will not coerce falls back to the declared default.

That tolerance is the contract, and it is deliberate. The file is **data, not code**: it is
hand-edited, it survives a release that retires a setting, and a stale or fat-fingered line
in it must never be able to stop the shell from starting. The failure it is written against
is real — retiring `server_port` once made every older config file raise `KeyError` at
import, before anything could print an error saying so.

Format is `configparser` with `ExtendedInterpolation`, so a value may name another:

    [paths]
    topics_dir = ${root_dir}/topics

Sections are for the reader's benefit only — they are flattened away, and a key repeated
across two of them is an error rather than a coin toss. The anchors a value may interpolate
(`root_dir`, `package_dir`, `secrets_dir`, `home_dir`) are computed, seeded in by the
caller, and are not themselves settings.

Stdlib-only and silent on stdout, like everything else this package puts on the git-filter
path.
"""
from __future__ import annotations

__all__ = ['ValuesError', 'coerce', 'flatten', 'read_sections', 'set_value']

import re
from configparser import ConfigParser, Error as ConfigParserError, ExtendedInterpolation
from pathlib import Path
from typing import Any


class ValuesError(Exception):
    """The values file said something contradictory — a duplicate key, or an unwritable one."""


def _parser(anchors: dict[str, str]) -> ConfigParser:
    """A parser seeded with the interpolation *anchors* and human-friendly comment rules."""
    parser = ConfigParser(defaults=anchors, interpolation=ExtendedInterpolation(),
                          inline_comment_prefixes=('#', ';'))
    parser.optionxform = str  # type: ignore[method-assign,assignment]  # keys are field names, verbatim
    return parser


def read_sections(path: Path, anchors: dict[str, str]) -> dict[str, dict[str, str]]:
    """Read *path* into `{section: {key: raw value}}`, or `{}` if it is unreadable.

    Args:
        path: The values file. A missing one is not an error — it means "every setting is
            its declared default", which is a working configuration.
        anchors: Computed values a line may interpolate as `${name}`. They are seeded as
            parser defaults, so they are visible from every section and are dropped on the
            way out: an anchor is not a setting.

    Sections are kept apart here because one of them, `[scripts]`, is a nested setting
    rather than a group of flat ones. :func:`flatten` folds the rest together.
    """
    parser = _parser(anchors)
    try:
        if not parser.read(path, encoding='utf-8'):
            return {}
    except (ConfigParserError, OSError, UnicodeDecodeError):
        return {}                                  # data, not code: never fatal at startup
    return {section: {key: raw for key, raw in parser.items(section) if key not in anchors}
            for section in parser.sections()}


def flatten(sections: dict[str, dict[str, str]], path: Path) -> dict[str, str]:
    """Fold *sections* into one `{key: raw value}` mapping.

    Sections are for the reader's benefit — which heading a setting is filed under says
    nothing about what it means, so the class sees one flat namespace.

    Raises:
        ValuesError: if a key appears in more than one section. Two lines claiming the same
            setting have no defensible winner, and silently taking the last one is how a
            configuration starts disagreeing with the file that describes it.
    """
    values: dict[str, str] = {}
    seen: dict[str, str] = {}
    for section, items in sections.items():
        for key, raw in items.items():
            if key in seen:
                raise ValuesError(f'{path}: `{key}` is set in both [{seen[key]}] and [{section}]')
            seen[key] = section
            values[key] = raw
    return values


def coerce(name: str, raw: str, declared: type) -> Any:
    """Coerce *raw* to the *declared* type of setting *name*.

    Raises:
        ValueError: if it will not convert — the caller keeps the declared default.
    """
    text = raw.strip()
    if declared is Path:
        if not text:
            raise ValueError(f'{name}: empty path')
        return Path(text).expanduser()
    if declared is bool:
        return text.lower() in {'1', 'true', 'yes', 'on'}
    if declared in (int, float, str):
        return declared(text)
    raise ValueError(f'{name}: no rule for reading a {declared.__name__} from the values file')


def set_value(path: Path, key: str, value: object) -> None:
    """Rewrite the single line assigning *key* in *path*, leaving the rest of the file alone.

    A whole-file rewrite through `ConfigParser.write` would round-trip the values and
    discard everything around them — the section headings, the comments saying why a number
    is what it is, the blank lines. Those are most of what makes the file worth hand-editing,
    so the one line that changes is the only one touched. Any trailing comment survives.

    Raises:
        ValuesError: if *key* is not already assigned in the file. A setting that is not in
            the catalogue is one the writer has no business inventing at the end of it.
    """
    text = path.read_text(encoding='utf-8')
    pattern = re.compile(rf'^(?P<lead>[ \t]*{re.escape(key)}[ \t]*=[ \t]*)'
                         r'(?P<value>[^#;\n]*?)(?P<trail>[ \t]*(?:[#;][^\n]*)?)$', re.MULTILINE)
    if (match := pattern.search(text)) is None:
        raise ValuesError(f'{path}: no `{key}` line to update')
    replacement = f'{match.group("lead")}{value}{match.group("trail")}'
    path.write_text(text[:match.start()] + replacement + text[match.end():], encoding='utf-8')
