#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" A set of utilities to manage Git repository workflows. """
from __future__ import annotations

from datetime import datetime
from subprocess import CalledProcessError, run
from tomllib import load
from typing import Literal

from solver.config import config
from solver.shell import console, register
from solver.utils.shell_utils import confirm


def run_cmdline(cmdline: str) -> int:
    """Run a shell command in the repository root and print its exit code.

    Args:
        cmdline: The shell command string to execute.
    """
    try:
        process = run(cmdline, shell=True, check=True, cwd=config.root_dir)
    except CalledProcessError as e:
        result: int = e.returncode
    else:
        result = process.returncode
    style = 'success' if result == 0 else 'error'
    console.print(f'[{style}]>[/{style}] [muted]{cmdline}[/muted] [{style}]→ {result}[/{style}]')
    return result


@register(name='commit',
          help='Commit solutions and workspace.',
          usage='commit [reset=false] [verify=true]', )
def commit(reset: bool = False, verify: bool = True) -> Literal['ok', 'nok']:
    """ Commit all changes in the local repository. """
    cmdline: list[str] = ['git', 'reset', '--soft', 'origin/master', '&&'] if reset else []
    cmdline += ['git', 'add', '-A', 'solutions', 'workspace', '&&']
    cmdline += ['git', 'commit', '-a'] if verify else ['git', 'commit', '-a', '--no-verify']
    cmdline += ['--message', f'"checkpoint {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"']
    result = run_cmdline(' '.join(cmdline))
    return 'nok' if result else 'ok'


@register(name='publish',
          help='Publish changed files for named targets to the remote repository.',
          usage='publish [keys|scripts|solutions|solver=solutions] [dry-run=false]', )
def git_publish(*targets: Literal['keys', 'scripts', 'solutions', 'solver'],
                dry_run: bool = False) -> Literal['ok', 'nok']:
    """Publish changed files for named targets to the remote repository.

    Args:
        targets: Scopes of files to publish — one or more of 'keys', 'scripts', 'solutions', or 'solver'.
                 Defaults to 'solutions'.
        dry_run: Print the push and pull-request commands instead of running them.  Defaults to False.

    Raises:
        ValueError: If any target is not one of the accepted values.
    """
    if not targets:
        targets = ('solutions',)
    if not all(target in ['keys', 'scripts', 'solutions', 'solver'] for target in targets):
        raise ValueError(f'Invalid targets: {", ".join(targets)}')
    if dry_run:
        result = run_cmdline(f'{config.scripts.publish} --dry-run {" ".join(targets)}')
    else:
        result = run_cmdline(f'{config.scripts.publish} {" ".join(targets)}')
    return 'nok' if result else 'ok'


@register(name='status',
          help='Display the sync state between the local branch and origin/master.',
          usage='status [details=false]', )
def git_status(details: bool = False) -> Literal['ok', 'nok']:
    """Display the sync state between the local branch and origin/master.

    Args:
        details:    When True, lists every differing file and uncommitted change.
                    When False (default), shows file counts only.
    """
    if details:
        result = run_cmdline(config.scripts.status)
    else:
        result = run_cmdline(f'{config.scripts.status} --summary')
    return 'nok' if result else 'ok'


@register(name='sync',
          help='Bring the local repository in sync with origin/master.',
          usage='sync [dry-run=false]', )
def git_sync(dry_run: bool = False) -> Literal['ok', 'nok']:
    """Bring the local repository in sync with origin/master.

    Args:
        dry_run: Print the sync commands instead of running them. Defaults to False.
    """
    if dry_run:
        result = run_cmdline(f'{config.scripts.sync} --dry-run')
    else:
        result = run_cmdline(config.scripts.sync)
    return 'nok' if result else 'ok'


@register(name='upgrade',
          help='Upgrade packages in the current venv for the given dependency groups.',
          usage='upgrade [all|ai|core|dev|solutions|show=all]', )
def pip_upgrade(*groups: Literal['all', 'ai', 'core', 'dev', 'solutions', 'show']) -> Literal['ok', 'nok']:
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
        return 'nok' if result else 'ok'
    else:
        console.print('[muted]Package upgrade cancelled.[/muted]')
        return 'nok'


@register(name='git-hooks',
          help='Run pre-commit hook and simulated pre-push hook.',
          usage='git-hooks',
          aliases=('hooks',), )
def pre_commit() -> Literal['ok', 'nok']:
    """Run pre-commit hooks."""
    console.print('[primary]Running pre-commit hooks...[/primary]')
    run_cmdline(config.root_dir.joinpath('.git/hooks/pre-commit').as_posix())
    console.print('[primary]Running simulated pre-push hooks...[/primary]')
    cmd_line = ('echo "refs/heads/master $(git rev-parse HEAD) refs/heads/master $(git rev-parse origin/master)" | '
                f'{config.root_dir.joinpath(".git/hooks/pre-push").as_posix()}')
    result = run_cmdline(cmd_line)
    return 'nok' if result else 'ok'


@register(name='install',
          help='Installs or uninstalls system resources.',
          usage='install <target> [uninstall=False] [show_help=False]',
          aliases=('setup',), )
def sys_install(target: Literal['chrome', 'dev-env', 'upgrade-service'],
                uninstall: bool = False,
                show_help: bool = False) -> Literal['ok', 'nok']:
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
        return 'nok' if result else 'ok'
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
        return 'nok' if result else 'ok'
    else:
        console.print('[muted]Installation cancelled.[/muted]')
        return 'nok'


__all__ = (
    'commit',
    'git_publish',
    'git_status',
    'git_sync',
    'pip_upgrade',
    'pre_commit',
    'sys_install',
)
