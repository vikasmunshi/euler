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

from solver.config import ExitCodes, config
from solver.shell import console, register
from solver.utils.shell_utils import confirm, run_cmdline


@register(
    requires='admin',
    help_text="Upgrade dependency group ([accent.dim]all[/accent.dim]|ai|core|dev|solutions|show).",
    aliases=('upgrade',),
)
def pip_upgrade(*groups: Literal['all', 'ai', 'core', 'dev', 'solutions', 'show']) -> int:
    """Upgrade packages in the current venv for the given dependency groups.

    Groups are defined in pyproject.toml:   'core' for project.dependencies,
                                            'ai', 'dev', 'solutions', 'show' for optional-dependencies,
                                            'all' to upgrade everything.
                                            Defaults to 'all'.

    Args:
        groups: One or more group names, or 'all'.
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
    if confirm(f'Upgrade {len(packages)} package(s): {" ".join(packages)}'):
        result = run_cmdline(f'{config.scripts.upgrade} {" ".join(packages)}')
        return result
    else:
        console.print('[muted]Package upgrade cancelled.[/muted]')
        return ExitCodes.EXIT_ERROR


@register(
    requires='admin',
    help_text='Installs or uninstalls system resources.',
    aliases=('install',),
)
def sys_setup(target: Literal['chrome', 'dev-env', 'upgrade-service'],
              uninstall: bool = False,
              show_help: bool = False) -> int:
    """ Installs or uninstalls the system resource specified as the target.

    Parameters:
        target:     Specifies the target resource to install or uninstall.
                    Accepted values are 'chrome', 'dev-env', and 'upgrade-service'
        uninstall:  Indicates whether the operation is an uninstallation.
                    Defaults to False, which performs installation.
        show_help:  Displays help information for the specified target.
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
    if confirm(f'{arg.capitalize()} {name}{extra_arg} (requires sudo)?'):
        result = run_cmdline(f'{script} {arg}{extra_arg}')
        return result
    else:
        console.print('[muted]Installation cancelled.[/muted]')
        return ExitCodes.EXIT_ERROR
