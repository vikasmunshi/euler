#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" A set of utilities to manage Git repository workflows. """
from __future__ import annotations

from pathlib import Path
from subprocess import CalledProcessError, run
from tomllib import load
from typing import Literal

from solver.core.config import Config
from solver.utils.path_utils import canonical_path
from solver.utils.shell_utils import confirm


def run_cmdline(cmdline: str) -> None:
    """Run a shell command in the repository root and print its exit code.

    Args:
        cmdline: The shell command string to execute.
    """
    try:
        process = run(cmdline, shell=True, check=True, cwd=Config.root_dir)
    except CalledProcessError as e:
        result: int = e.returncode
    else:
        result = process.returncode
    print(f'{Config.ColorCodes.GREEN if result == 0 else Config.ColorCodes.RED}'
          f'> {cmdline} -> {result}'
          f'{Config.ColorCodes.RESET}')


def build_c() -> None:
    """Build all C source files in the workspace directory."""
    source_files: list[Path] = sorted(s for s in Config.workspace_dir.iterdir() if s.is_file() and s.suffix == '.c')
    for source_file in source_files:
        cmdline: str = f'{Config.ScriptPaths.BUILD_C} {canonical_path(source_file)}'
        process = run(cmdline, capture_output=True, cwd=Config.root_dir, shell=True, text=True)
        if process.returncode != 0:
            print(f'{Config.ColorCodes.RED}Error building {source_file.name}{Config.ColorCodes.RESET}\n'
                  f'{process.stdout}{'\n' if process.stdout and process.stderr else ''} {process.stderr}')


def commit() -> None:
    """ Commit all changes in the local repository. """
    cmdline = 'git reset --soft origin/master && git commit -a -m "auto-commit"'
    run_cmdline(cmdline)


def git_publish(*targets: Literal['keys', 'scripts', 'solutions', 'solver'],
                dry_run: bool = False) -> None:
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
        run_cmdline(f'{Config.ScriptPaths.PUBLISH} --dry-run {" ".join(targets)}')
    else:
        run_cmdline(f'{Config.ScriptPaths.PUBLISH} {" ".join(targets)}')


def git_status(details: bool = False) -> None:
    """Display the sync state between the local branch and origin/master.

    Args:
        details:    When True, lists every differing file and uncommitted change.
                    When False (default), shows file counts only.
    """
    if details:
        run_cmdline(Config.ScriptPaths.STATUS)
    else:
        run_cmdline(f'{Config.ScriptPaths.STATUS} --summary')


def git_sync(dry_run: bool = False) -> None:
    """Bring the local repository in sync with origin/master.

    Args:
        dry_run: Print the sync commands instead of running them. Defaults to False.
    """
    if dry_run:
        run_cmdline(f'{Config.ScriptPaths.SYNC} --dry-run')
    else:
        run_cmdline(Config.ScriptPaths.SYNC)


def pip_upgrade(*groups: Literal['all', 'ai', 'core', 'dev', 'solutions', 'show']) -> None:
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
    with open(Config.root_dir / 'pyproject.toml', 'rb') as f:
        data = load(f)
    available: dict[str, list[str]] = {'core': data['project']['dependencies']}
    available.update(data['project'].get('optional-dependencies', {}))
    if 'all' in groups:
        packages: list[str] = [p for pkgs in available.values() for p in pkgs]
    else:
        packages = [p for name in groups for p in available[name]]
    if confirm(f'Upgrade {len(packages)} package(s): {" ".join(packages)}'):
        run_cmdline(f'{Config.ScriptPaths.UPGRADE} {" ".join(packages)}')
    else:
        print('Package upgrade cancelled.')


def pre_commit() -> None:
    """Run pre-commit hooks."""
    print('Running pre-commit hooks...')
    run_cmdline(Config.root_dir.joinpath('.git/hooks/pre-commit').as_posix())
    print('Running simulated pre-push hooks...')
    cmd_line = ('echo "refs/heads/master $(git rev-parse HEAD) refs/heads/master $(git rev-parse origin/master)" | '
                f'{Config.root_dir.joinpath(".git/hooks/pre-push").as_posix()}')
    run_cmdline(cmd_line)


def sys_install(target: Literal['chrome', 'dev-env', 'upgrade-service'],
                uninstall: bool = False,
                show_help: bool = False) -> None:
    """ Installs or uninstalls the system resource specified as the target.

    Parameters:
        target:     Specifies the target resource to install or uninstall.
                    Accepted values are 'chrome', 'dev-env', and 'upgrade-service'
        uninstall:  Indicates whether the operation is an uninstallation.
                    Defaults to False, which performs installation.
        show_help:  Displays help information for the specified target.
    """
    script: str = {
        'chrome': Config.ScriptPaths.INSTALL_CHROME,
        'dev-env': Config.ScriptPaths.INSTALL_DEV_ENV,
        'upgrade-service': Config.ScriptPaths.INSTALL_UPGRADE_SERVICE,
    }[target]
    arg: str = '--help' if show_help else 'uninstall' if uninstall else 'install'
    if show_help:
        run_cmdline(f'{script} {arg}')
        return
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
        run_cmdline(f'{script} {arg}{extra_arg}')


__all__ = (
    'build_c',
    'commit',
    'git_publish',
    'git_status',
    'git_sync',
    'pip_upgrade',
    'pre_commit',
    'sys_install',
)
