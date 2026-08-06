#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Configuration: `from solver.config import config` — the one way in.

The package is split by *what a value is*, not by who reads it:

- :mod:`~solver.config.paths` — the two anchors (`package_root`, `repo_root()`) and the
  shell's explicit `enter_repo()`. Stdlib-only; the git-filter path may import it.
- :mod:`~solver.config.config` — the static settings: every path and constant, and the
  `Config` class that holds them. Imports stdlib, `solver.version` and this package only.
- :mod:`~solver.config.identity` — dynamic: the resolved `Subject`, and per-user state.
- :mod:`~solver.config.theme` — dynamic: the `rich` theme and `prompt_toolkit` style.

The dynamic modules are reached only through `cached_property` on `Config`, so importing
configuration stays pure: no chdir, no `PATH` edit, no identity resolution, no `rich`.

.. note::
   The line order below is load-bearing. `solver.config.config` is a submodule of this
   package, so importing it binds the name `config` **on this package** to that module;
   the assignment underneath rebinds it to the singleton, which is what every
   `from solver.config import config` must get. Python guarantees this runs before any
   outside importer can observe either name — a submodule cannot be imported without its
   parent package being fully executed first. `tests/test_config.py` pins the invariant.
"""
from __future__ import annotations

__all__ = ['Config', 'ExitCodes', 'REPO_ROOT_ENV', 'config', 'enter_repo', 'package_root', 'repo_root']

from solver.config.config import Config, ExitCodes
from solver.config.paths import REPO_ROOT_ENV, enter_repo, package_root, repo_root

#: The process-wide configuration singleton. Constructing it reads no identity and moves
#: no process (see the module docstring), so import order carries no surprises.
config: Config = Config()
