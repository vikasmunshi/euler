#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Dependency, system-resource and per-user tool setup commands.

The venv dependency upgrade (`pip-upgrade`) and the system-resource installer
(`sys-setup`) — both `admin`-floor — and the per-user tool installer (`tool-setup`,
`contributor`-floor: it installs into the caller's own home, no sudo). All shell out to
the setup scripts under `scripts/`. The git and GitHub workflow commands live in
:mod:`solver.core.git`.
"""
from __future__ import annotations

from importlib.util import find_spec
from tomllib import load
from typing import Annotated, Any, Literal

from solver.config import config
from solver.shell import console, register
from solver.shell.dialogue import Abort, Ask, confirm
from solver.utils.shell_utils import run_cmdline


#: The web tier's packages: their dependencies make up the `web` group of `pip-upgrade`.
_WEB_PACKAGES: tuple[str, ...] = ('site', 'webshell')


def _dependency_groups() -> dict[str, list[str]]:
    """Every package's dependencies by group, the lockstep `euler-*` pins left out."""
    def read(package: str) -> dict[str, Any]:
        with open(config.root_dir / 'packages' / package / 'pyproject.toml', 'rb') as f:
            project: dict[str, Any] = load(f)['project']
        return project

    solver = read('solver')
    groups: dict[str, list[str]] = {'core': solver['dependencies'], **solver.get('optional-dependencies', {})}
    groups['web'] = [d for package in _WEB_PACKAGES for d in read(package).get('dependencies', [])
                     if not d.startswith('euler-')]
    return groups


@register(requires='admin', aliases=('upgrade',))
def pip_upgrade(*groups: Literal['all', 'ai', 'core', 'dev', 'solutions', 'show', 'web']) -> int:
    """Upgrade packages in the current venv for the given dependency groups.

    Groups are read from the packages' pyproject.toml files:
        'core' for euler-solver's project.dependencies,
        'ai', 'dev', 'solutions', 'show' for its optional-dependencies,
        'web' for euler-site's and euler-webshell's dependencies,
        'all' to upgrade everything ('web' only when the web tier is installed in this venv).
        Defaults to 'all'.

    Args:
        *groups: One or more dependency group names, or 'all'.
    """
    if not groups:
        groups = ('all',)
    available = _dependency_groups()
    if 'all' in groups:
        names = [name for name in available if name != 'web' or find_spec('euler_site') is not None]
    else:
        names = list(groups)
    packages: list[str] = list(dict.fromkeys(p for name in names for p in available[name]))
    console.print(f'[muted]{" ".join(packages)}[/muted]')
    if not confirm(f'Upgrade {len(packages)} package(s)?', default=True):
        raise Abort('upgrade cancelled')
    return run_cmdline(f'{config.scripts.upgrade} {" ".join(packages)}')


#: What each resource is, for the menu the adapter puts when one is left out.
_RESOURCES: dict[str, str] = {
    'chrome': 'the browser `show` and `edit` drive',
    'dev-env': 'the apt packages, the venv, the hooks, completions, Node.js',
    'upgrade-service': 'the unattended-upgrade timer',
}


@register(requires='admin', aliases=('install',))
def sys_setup(target: Annotated[Literal['chrome', 'dev-env', 'upgrade-service'],
                                Ask('Which resource?', labels=_RESOURCES)],
              uninstall: bool = False,
              show_help: bool = False) -> int:
    """Install or uninstall a system resource.

    Runs the setup script for *target* under `sudo`, after confirming. Each script is
    idempotent, so re-running an install is safe.

    Args:
        target: [asked] Which resource to act on: 'chrome', 'dev-env' or
            'upgrade-service'. Offered as a menu when omitted.
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


#: What each per-user tool is, for the menu the adapter puts when one is left out.
_TOOLS: dict[str, str] = {
    'claude': 'the Claude Code CLI, in ~/.local/bin',
}


@register(requires='contributor')
def tool_setup(tool: Annotated[Literal['claude'], Ask('Which tool?', labels=_TOOLS)],
               action: Literal['install', 'uninstall', 'reinstall'] = 'install') -> int:
    """Install, uninstall or reinstall a per-user tool in your own home.

    Runs the tool's setup script as you — no sudo: the tool lands under your home
    (`~/.local/bin`), with your own login and config, so the floor is `contributor`, not
    `admin` like `sys-setup`. On the web host the download goes through the egress proxy.
    An install of a tool already there is a no-op; uninstall and reinstall ask first.

    Args:
        tool: [asked] Which tool: 'claude' (Claude Code). Offered as a menu when omitted.
        action: 'install', 'uninstall', or 'reinstall' (uninstall, then install).
            Defaults to 'install'.
    """
    script: str = {
        'claude': config.scripts.install_claude,
    }[tool]
    if action != 'install' and not confirm(f'{action.capitalize()} {_TOOLS[tool]}?', default=False):
        raise Abort(f'{action} cancelled')
    if action in ('uninstall', 'reinstall') and (rc := run_cmdline(f'{script} uninstall')) != 0:
        return rc
    return 0 if action == 'uninstall' else run_cmdline(f'{script} install')
