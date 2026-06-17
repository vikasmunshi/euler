#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility for loading modules. """
from __future__ import annotations

__all__ = ['load_commands', 'update_modules']

import csv
import importlib
import re
from typing import Literal

from solver.config import config
from solver.shell.tty import console
from solver.utils.path_utils import canonical_path, iterdir_recursive

_commands_loaded = False


def update_modules() -> bool:
    registers_commands_re = re.compile(r'^@(?:register|command)\(', re.MULTILINE)

    # Preserve any manual on/off edits: keep the existing `load` cell for known
    # modules, default new ones to whether they register commands, drop deleted ones.
    existing: dict[str, str] = {}
    if config.modules_file.exists():
        with open(config.modules_file, 'r', newline='') as f:
            existing = {row[0]: row[2] for row in csv.reader(f) if len(row) == 3}

    updated: dict[str, str | Literal[True]] = {'module': 'load'}
    with open(config.modules_file, 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['module', 'registers_commands', 'load'])
        for file in sorted(iterdir_recursive(config.modules_file.parent, rt='path')):
            if file.suffix != '.py':
                continue
            if file.stem.startswith('_'):
                continue
            code = file.read_text()
            registers = (registers_commands_re.search(code) is not None) or ''
            module = canonical_path(file.with_suffix('')).replace('/', '.')
            load = existing.get(module, registers)
            writer.writerow([module, registers, load])
            updated[module] = load

    return updated != existing


def load_commands(refresh_modules: bool = False) -> None:
    """Import the built-ins and every command module (once), populating the registry."""
    global _commands_loaded
    if _commands_loaded and not refresh_modules:
        return

    def is_on(cell: str) -> bool:
        """A module loads unless its `load` cell is blank/false/0/no/off (the manual switch)."""
        return cell.strip().lower() not in ('', 'false', '0', 'no', 'off')

    if refresh_modules or (not config.modules_file.exists()):
        update_modules()

    with open(config.modules_file, 'r', newline='') as f:
        _ = next(csv.reader(f))
        modules: list[str] = [name for name, registers, load in csv.reader(f) if is_on(registers) and is_on(load)]

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
