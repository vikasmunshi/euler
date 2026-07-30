#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Dependency and system-resource setup commands.

The venv dependency upgrade (`pip-upgrade`) and the system-resource installer
(`sys-setup`) — both `admin`-floor, both shelling out to the setup scripts under
`scripts/`. The git and GitHub workflow commands live in :mod:`solver.core.git`.
"""
from __future__ import annotations

from tomllib import load
from typing import Literal

from solver.config import config
from solver.shell import console, register
from solver.shell.dialogue import Abort, confirm
from solver.utils.shell_utils import run_cmdline


@register(requires='admin', aliases=('upgrade',))
def pip_upgrade(*groups: Literal['all', 'ai', 'core', 'dev', 'solutions', 'show']) -> int:
    """Upgrade packages in the current venv for the given dependency groups.

    Groups are defined in pyproject.toml:   'core' for project.dependencies,
                                            'ai', 'dev', 'solutions', 'show' for optional-dependencies,
                                            'all' to upgrade everything.
                                            Defaults to 'all'.

    Args:
        *groups: One or more dependency group names, or 'all'.
    """
    if not groups:
        groups = ('all',)
    with open(config.root_dir / 'pyproject.toml', 'rb') as f:
        data = load(f)
    available: dict[str, list[str]] = {'core': data['project']['dependencies']}
    available.update(data['project'].get('optional-dependencies', {}))
    if 'all' in groups:
        packages: list[str] = [p for pkgs in available.values() for p in pkgs]
    else:
        packages = [p for name in groups for p in available[name]]
    console.print(f'[muted]{" ".join(packages)}[/muted]')
    if not confirm(f'Upgrade {len(packages)} package(s)?', default=True):
        raise Abort('upgrade cancelled')
    return run_cmdline(f'{config.scripts.upgrade} {" ".join(packages)}')


@register(requires='admin', aliases=('install',))
def sys_setup(target: Literal['chrome', 'dev-env', 'upgrade-service'],
              uninstall: bool = False,
              show_help: bool = False) -> int:
    """Install or uninstall a system resource.

    Runs the setup script for *target* under `sudo`, after confirming. Each script is
    idempotent, so re-running an install is safe.

    Args:
        target: Which resource to act on: 'chrome', 'dev-env' or 'upgrade-service'.
        uninstall: Uninstall the target instead of installing it. Defaults to False.
        show_help: Print the target script's own help and stop, doing nothing else.
            Defaults to False.
    """
    script: str = {
        'chrome': config.scripts.install_chrome,
        'dev-env': config.scripts.install_dev_env,
        'upgrade-service': config.scripts.install_upgrade_service,
    }[target]
    arg: str = '--help' if show_help else 'uninstall' if uninstall else 'install'
    if show_help:
        result = run_cmdline(f'{script} {arg}')
        return result
    name: str = {
        'chrome': 'Chrome browser',
        'dev-env': 'development environment',
        'upgrade-service': 'system upgrade service',
    }[target]
    extra_arg: str = {
        'chrome': '',
        'dev-env': ' python primesieve c',
        'upgrade-service': '',
    }[target]
    if not confirm(f'{arg.capitalize()} {name}{extra_arg}? This needs sudo.', default=True):
        raise Abort(f'{arg} cancelled')
    return run_cmdline(f'{script} {arg}{extra_arg}')
