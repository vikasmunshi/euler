#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Utility for loading command modules.

``modules.csv`` is a pure **loader manifest** (DD-12): two columns
``(module, registers_commands)``. Every command-registering module is imported;
which of its commands actually **register** is decided per-command by the
``@register``/``@command`` decorator against the current subject's channel and
permissions — channel/profile gating no longer lives here.
"""
from __future__ import annotations

__all__ = ['load_commands', 'update_modules']

import csv
import importlib
import re

from solver.config import config
from solver.shell.tty import console
from solver.utils.path_utils import canonical_path, iterdir_recursive

_TRUTHY = ('true', '1', 'yes')
_commands_loaded = False


def update_modules() -> bool:
    """Regenerate ``modules.csv`` by scanning the package; True if the set changed.

    Each non-underscore ``.py`` module under the registry directory gets a row
    recording whether it registers commands (an ``@register``/``@command``
    decorator). Rows for deleted modules are dropped, new modules added.
    """
    registers_re = re.compile(r'^@(?:register|command)\(', re.MULTILINE)

    existing: dict[str, str] = {}
    if config.modules_file.exists():
        with open(config.modules_file, 'r', newline='') as f:
            existing = {row[0]: (row[1] if len(row) > 1 else '') for row in csv.reader(f)}

    updated: dict[str, str] = {'module': 'registers_commands'}
    with open(config.modules_file, 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['module', 'registers_commands'])
        for file in sorted(iterdir_recursive(config.modules_file.parent, rt='path')):
            if file.suffix != '.py' or file.stem.startswith('_'):
                continue
            registers = 'True' if registers_re.search(file.read_text()) else ''
            module = canonical_path(file.with_suffix('')).replace('/', '.')
            writer.writerow([module, registers])
            updated[module] = registers

    return updated != existing


def load_commands(refresh_modules: bool = False) -> None:
    """Import every command-registering module (once), populating the registry.

    All such modules are imported; per-command channel/permission gating happens
    in the decorator against ``config.subject``.
    """
    global _commands_loaded
    if _commands_loaded and not refresh_modules:
        return

    if refresh_modules or not config.modules_file.exists():
        update_modules()

    with open(config.modules_file, 'r', newline='') as f:
        _ = next(csv.reader(f))
        modules = [row[0] for row in csv.reader(f)
                   if len(row) > 1 and row[1].strip().lower() in _TRUTHY]

    for mod in modules:
        try:
            importlib.import_module(mod)
        except ImportError as e:
            console.print(f'[error]Failed to import {mod}: {e}')
        else:
            if refresh_modules:
                console.print(f'[success]Loaded {mod}')

    _commands_loaded = True


if __name__ == '__main__':
    load_commands(refresh_modules=True)
