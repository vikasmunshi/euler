#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Utility for loading modules. """
from __future__ import annotations

__all__ = ['Profile', 'load_commands', 'update_modules']

import csv
import importlib
import re
from typing import Literal

from solver.config import config
from solver.shell.tty import console
from solver.utils.path_utils import canonical_path, iterdir_recursive

#: Which SolverShell profile the modules are loaded for. The `terminal` profile
#: loads the full command set; the `web` profile drops commands that only make
#: sense on the machine running the shell (e.g. `show`, which opens a local
#: browser and cannot reach the user's desktop from a remote web front end).
Profile = Literal['terminal', 'web']

#: Zero-based index of each profile's on/off column in `modules.csv`
#: (`module, registers_commands, terminal, web`).
_PROFILE_COLUMN: dict[Profile, int] = {'terminal': 2, 'web': 3}

_commands_loaded = False


def update_modules(profile: Profile) -> bool:
    """Regenerate `modules.csv` by scanning the package.

    Returns True if the set of modules loaded for *profile* changed (a web-only
    edit therefore does not force a terminal shell to reload, and vice versa).

    Each non-underscore `.py` module under the registry directory gets a row
    recording whether it registers commands (an `@register`/`@command` decorator)
    and, per profile (`terminal`, `web`), whether it should load. Manual on/off
    edits for known modules are preserved, new modules default both profile cells
    to whether they register commands, and rows for deleted modules are dropped.
    """
    registers_commands_re = re.compile(r'^@(?:register|command)\(', re.MULTILINE)

    # Preserve any manual on/off edits: keep the existing `(terminal, web)` cells
    # for known modules, default new ones to whether they register commands, drop
    # deleted ones. The header row survives the round trip as ('terminal', 'web').
    existing: dict[str, tuple[str, str]] = {}
    if config.modules_file.exists():
        with open(config.modules_file, 'r', newline='') as f:
            existing = {row[0]: (row[2], row[3]) for row in csv.reader(f) if len(row) == 4}

    updated: dict[str, tuple[str | Literal[True], str | Literal[True]]] = {'module': ('terminal', 'web')}
    with open(config.modules_file, 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['module', 'registers_commands', 'terminal', 'web'])
        for file in sorted(iterdir_recursive(config.modules_file.parent, rt='path')):
            if file.suffix != '.py':
                continue
            if file.stem.startswith('_'):
                continue
            code = file.read_text()
            registers = (registers_commands_re.search(code) is not None) or ''
            module = canonical_path(file.with_suffix('')).replace('/', '.')
            cells = existing.get(module, (registers, registers))
            writer.writerow([module, registers, *cells])
            updated[module] = cells

    # Compare only the requested profile's column, so a change confined to the
    # other profile does not report as a change for this one.
    i = _PROFILE_COLUMN[profile] - 2
    return {m: c[i] for m, c in updated.items()} != {m: c[i] for m, c in existing.items()}


def load_commands(profile: Profile, refresh_modules: bool = False) -> None:
    """Import the built-ins and every command module (once), populating the registry.

    Only modules whose *profile* cell (`terminal` or `web`) is on are imported.
    """
    global _commands_loaded
    if _commands_loaded and not refresh_modules:
        return

    def is_on(cell: str) -> bool:
        """A module loads unless its cell is blank/false/0/no/off (the manual switch)."""
        return cell.strip().lower() not in ('', 'false', '0', 'no', 'off')

    if refresh_modules or (not config.modules_file.exists()):
        update_modules(profile)

    column = _PROFILE_COLUMN[profile]
    with open(config.modules_file, 'r', newline='') as f:
        _ = next(csv.reader(f))
        modules: list[str] = [row[0] for row in csv.reader(f) if is_on(row[1]) and is_on(row[column])]

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
    load_commands('terminal', refresh_modules=True)
