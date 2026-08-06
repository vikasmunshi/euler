#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Configuration: `from solver.config import config` — the one way in.

The package is split by *what a value is*, not by who reads it:

- :mod:`~solver.config.paths` — the anchors (`package_root`, `repo_root()`, `share_file()`)
  and the shell's explicit `enter_repo()`. Stdlib-only.
- :mod:`~solver.config.settings` — every path and constant, and the `Config` class that
  holds them. Imports stdlib, `solver.version` and this package only.
- :mod:`~solver.config.values` — reading `values.conf`, the editable half.
- :mod:`~solver.config.env` — reading `env.conf`: the environment variable and default
  behind each web service's runtime settings.
- :mod:`~solver.config.identity` — dynamic: the resolved `Subject`, and per-user state.
- :mod:`~solver.config.theme` — dynamic: the `rich` theme and `prompt_toolkit` style.

**Importing a submodule builds nothing.** `config` is resolved on first access, not at
import, and that is load-bearing rather than tidy: `euler-auth`, `euler-msg` and
`euler-ws` run from `/opt/euler` with no working tree and no `EULER_REPO_ROOT`, so
`repo_root()` raises for them by design. They read `env.conf` through
:mod:`~solver.config.env`, and must be able to do so without a `Config` being constructed
underneath them. An eager singleton here would take euler-auth down at import — and Caddy
authenticates every request through euler-auth, so the site would go with it (that outage
is on the record: web-server-guide §11).

The static module is `settings`, not `config`, for the same reason in a different key: a
submodule named `config` would bind itself over this package's `config` attribute the
first time anything imported it by path, and every `from solver.config import config`
after that would quietly receive a module. `tests/test_config.py` pins both properties.
"""
from __future__ import annotations

__all__ = ['Config', 'ExitCodes', 'REPO_ROOT_ENV', 'SHARE_FILE_ENV', 'ValuesError', 'build_config',
           'config', 'enter_repo', 'package_root', 'repo_root', 'settable_fields', 'share_file']

from typing import TYPE_CHECKING, Any

from solver.config.paths import REPO_ROOT_ENV, SHARE_FILE_ENV, enter_repo, package_root, repo_root, share_file
from solver.config.settings import Config, ExitCodes, ValuesError, build_config, settable_fields

if TYPE_CHECKING:  # the singleton, for checkers; at runtime it arrives via __getattr__
    config: Config


def __getattr__(name: str) -> Any:
    """Resolve `config` on first access, and cache it as a real module global.

    The rebinding into `globals()` is what keeps this to one construction: after the first
    read, ordinary attribute lookup finds the instance and this function is never called
    for it again.
    """
    if name == 'config':
        instance = build_config()
        globals()['config'] = instance
        return instance
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
