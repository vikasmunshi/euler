#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" A set of utilities to manage Git repository workflows.

Per-user native git (docs/web-server-guide.md § Git): a collaborator's shell runs in
**their own clone** on branch ``user/<slug>`` as their own uid, so git needs no
broker — the read verbs (`git-status`, `git-sync`) are ``reader``-floor and the
write verbs (`git-commit`, `git-push`, `git-hooks`) are ``contributor``-floor; the
blast radius is their own branch. ``master`` stays admin-gated: `git-merge` is the
one gate through which a ``user/<slug>`` branch lands on master.
"""
from __future__ import annotations

import sys
from datetime import datetime
from subprocess import CalledProcessError, DEVNULL, run
from tomllib import load
from typing import Literal

from solver.config import ExitCodes, config
from solver.crypto.ciphers import read_master_key
from solver.crypto.config import config as crypto_config
from solver.shell import console, register
from solver.utils.shell_utils import confirm


def run_cmdline(cmdline: str) -> int:
    """Run a shell command in the repository root and print its exit code.

    Args:
        cmdline: The shell command string to execute.
    """
    pipe = DEVNULL if console.quiet else None
    try:
        process = run(cmdline, shell=True, check=True, cwd=config.root_dir, stdout=pipe, stderr=pipe, )
    except CalledProcessError as e:
        result: int = e.returncode
    else:
        result = process.returncode
    return result


def _current_branch() -> str:
    """The checked-out branch name ('' when detached or not a repo)."""
    proc = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
               cwd=config.root_dir, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ''


@register(requires='contributor',
          help_text='Commit everything, optionally resetting to origin/master.', aliases=('commit',), quietable=True, )
def git_commit(reset: bool = False, verify: bool = True, message: str = '') -> int:
    """Stage and commit the solutions and solver package as a timestamped checkpoint.

    Adds everything under `solutions/` and `solver/` and commits it with a
    `checkpoint <timestamp>` message — the routine "save my progress" step.

    Args:
        reset:  When True, first soft-reset to `origin/master` so the new commit
                squashes all local commits into a single checkpoint (working
                tree untouched). Defaults to False.
        verify: When True (default), run the pre-commit hook (flake8 + mypy).
                When False, commit with `--no-verify`, skipping the hook.
        message: The commit message. When empty (default), a
                 `checkpoint <timestamp>` message is used.

    Aliased as `commit`.
    """
    text: str = message or f'checkpoint {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    cmdline: list[str] = ['git', 'reset', '--soft', 'origin/master', '&&'] if reset else []
    cmdline += ['git', 'add', '-A', 'solutions', 'solver', '&&']
    cmdline += ['git', 'commit', '-a'] if verify else ['git', 'commit', '-a', '--no-verify']
    cmdline += ['--message', f'"{text}"']
    result = run_cmdline(' '.join(cmdline))
    return result


@register(
    requires='admin',
    help_text='Push targets (keys|scripts|[accent]solutions[/accent]|solver) to remote.',
    aliases=('publish',),
    quietable=True,
)
def git_publish(*targets: Literal['keys', 'scripts', 'solutions', 'solver'],
                dry_run: bool = False) -> int:
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
    return result


@register(requires='reader',
          help_text='Display sync state between local and origin/master.', aliases=('status',),)
def git_status(details: bool = False) -> int:
    """Display the sync state between the local branch and origin/master.

    Args:
        details:    When True, lists every differing file and uncommitted change.
                    When False (default), shows file counts only.
    """
    if details:
        result = run_cmdline(config.scripts.status)
    else:
        result = run_cmdline(f'{config.scripts.status} --summary')
    return result


def _enc_key_pull_flow() -> None:
    """The self-service tail of a sync: wire the git filter once key access exists.

    A provisioned clone starts filter-UNWIRED with ``solutions/private/**`` as
    ciphertext. When a pull delivers a ``keys/enc-key.json`` that wraps the master key to
    this user's public key (an admin ran ``user-authorize`` and pushed), wire the
    clean/smudge filter and re-checkout the private tree — ciphertext becomes plaintext
    in place. A silent no-op while the filter is already wired or the user is not (yet)
    key-authorized, so every sync may call it.
    """
    name: str = crypto_config['filter_name']
    wired: bool = run(['git', 'config', '--local', '--get', f'filter.{name}.process'],
                      cwd=config.root_dir, capture_output=True).returncode == 0
    if wired:
        return
    read_master_key.cache_clear()               # this very pull may have delivered access
    try:
        read_master_key()
    except (FileNotFoundError, KeyError, ValueError):
        return                                  # no keypair / not authorized — nothing to do
    console.print('[primary]Master-key access detected — wiring the git filter and '
                  'decrypting private solutions...[/primary]')
    if run_cmdline(f'{sys.executable} -m solver.crypto.gitfilter install') == 0:
        run_cmdline('git ls-files -z -- solutions/private | xargs -0 -r rm -f -- '
                    '&& git checkout -- solutions/private')


@register(requires='reader', aliases=('filter',),
          help_text='Wire the git encryption filter: [accent.dim]status[/accent.dim] | install.')
def git_filter(action: Literal['status', 'install'] = 'status') -> int:
    """Report or wire the transparent encryption filter for `solutions/private`.

    `status` shows the filter wiring and whether this session can unwrap the
    master key. `install` verifies master-key access first (refusing cleanly
    without it — nothing is wired), registers the clean/smudge filter in this
    clone's git config, and re-checks out `solutions/private` so existing
    ciphertext decrypts in place. The explicit form of what `git-sync` runs
    automatically after a pull that delivers key access — use it when access
    arrived some other way, e.g. right after `key-reconstruct` from shares.

    Args:
        action: 'status' (default) or 'install'.

    Aliased as `filter`.
    """
    if action == 'status':
        return run_cmdline(f'{sys.executable} -m solver.crypto.gitfilter status')
    result = run_cmdline(f'{sys.executable} -m solver.crypto.gitfilter install')
    if result != 0:
        return result
    # Re-smudge: existing ciphertext in the worktree only decrypts on a fresh
    # checkout. Genuine local edits must not be clobbered — but a freshly wired
    # clone is NOT dirty (clean() passes ciphertext through, matching the stored
    # blob), so the guard only trips on real plaintext changes.
    dirty: str = run(['git', 'status', '--porcelain', '--', 'solutions/private'],
                     cwd=config.root_dir, capture_output=True, text=True).stdout.strip()
    if dirty:
        console.print('[warning]solutions/private has local changes — skipping the re-checkout; '
                      'commit or stash, then run [accent]git-filter install[/accent] again.[/warning]')
        return int(ExitCodes.EXIT_OK)
    console.print('[primary]Decrypting private solutions in place...[/primary]')
    return run_cmdline('git ls-files -z -- solutions/private | xargs -0 -r rm -f -- '
                       '&& git checkout -- solutions/private')


@register(requires='reader',
          help_text='Bring the local repository in sync with origin/master.', aliases=('sync',),)
def git_sync(dry_run: bool = False) -> int:
    """Bring the local repository in sync with origin/master.

    On a per-user clone (branch `user/<slug>`) this is the pull flow: fetch
    origin/master and merge/rebase it into your branch — bringing in merged work
    and, notably, `keys/enc-key.json`. When that pull first delivers master-key
    access for your key, the git filter is wired automatically and the private
    solutions decrypt in place.

    Args:
        dry_run: Print the sync commands instead of running them. Defaults to False.
    """
    if dry_run:
        result = run_cmdline(f'{config.scripts.sync} --dry-run')
    else:
        result = run_cmdline(config.scripts.sync)
        if result == 0:
            _enc_key_pull_flow()
    return result


@register(requires='contributor',
          help_text='Sign in to GitHub (gh) and set this clone\'s git identity from it.',
          aliases=('identity',),)
def git_identity() -> int:
    """Configure your git identity and push credential from your GitHub login.

    The one-time setup before `git-push`: runs `gh auth login` when you are not yet
    signed in (interactive device flow — works in the web shell), makes gh the git
    credential helper (`gh auth setup-git`), and sets this clone's `user.name` /
    `user.email` from your GitHub profile, so your commits are authored and pushed
    as **you**, never as a service identity.

    Aliased as `identity`.
    """
    return run_cmdline(config.scripts.configure_identity)


@register(requires='contributor', quietable=True,
          help_text='Push the current branch to origin (your own user/<slug> branch).', aliases=('push',),)
def git_push(force: bool = False) -> int:
    """Push the current branch to origin as yourself (`git push -u origin <branch>`).

    In a per-user clone the current branch is `user/<slug>`, pushed with your own
    GitHub identity — `git-identity` is the one-time setup. Landing work on master
    is the admin's `git-merge`, never a direct push: pushing master requires
    the `admin` floor, and force-pushing it is always refused.

    Args:
        force: Push with `--force-with-lease` — needed after `git-sync` rebased your
               branch onto a moved origin/master. Refused on master.
    """
    branch: str = _current_branch()
    if not branch or branch == 'HEAD':
        console.print('[error]error:[/error] no branch checked out.')
        return ExitCodes.EXIT_ERROR
    if branch == 'master':
        if force:
            console.print('[error]error:[/error] force-pushing master is never allowed.')
            return ExitCodes.EXIT_ERROR
        if not config.subject.has('admin'):
            console.print('[error]error:[/error] pushing master needs the [accent]admin[/accent] profile; '
                          'your work belongs on your own user/<slug> branch.')
            return ExitCodes.EXIT_ERROR
    lease: str = ' --force-with-lease' if force else ''
    return run_cmdline(f'git push -u{lease} origin {branch}')


@register(requires='admin', quietable=True,
          help_text="Merge a collaborator's user/<slug> branch into master and push.", aliases=('merge',),)
def git_merge(branch: str, push: bool = True) -> int:
    """Merge a collaborator's branch into master — the one gate to master.

    Fetches the branch from origin and merges it `--no-ff` into the checked-out
    master; a conflicted merge is aborted and reported (resolve it manually). On a
    clean merge, master is pushed (the collaborator's next `git-sync` then rebases
    their branch onto it).

    Args:
        branch: The branch to merge; a bare `<slug>` means `user/<slug>`.
        push:   Push master to origin after a clean merge. Defaults to True.
    """
    if '/' not in branch:
        branch = f'user/{branch}'
    if _current_branch() != 'master':
        console.print('[error]error:[/error] merges land on master — check out master first.')
        return ExitCodes.EXIT_ERROR
    if run_cmdline(f'git fetch origin {branch}') != 0:
        console.print(f'[error]error:[/error] cannot fetch [accent]origin/{branch}[/accent].')
        return ExitCodes.EXIT_ERROR
    if run_cmdline(f'git merge --no-ff -m "merge {branch}" origin/{branch}') != 0:
        run_cmdline('git merge --abort')
        console.print(f'[error]error:[/error] merging [accent]origin/{branch}[/accent] conflicts; '
                      'aborted — merge and resolve manually.')
        return ExitCodes.EXIT_ERROR
    return run_cmdline('git push origin master') if push else int(ExitCodes.EXIT_OK)


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
    requires='contributor',
    help_text='Run pre-commit hook and simulated pre-push hook.',
    aliases=('hooks',),
    quietable=True,
)
def git_hooks() -> int:
    """Run the git pre-commit and (simulated) pre-push checks on demand.

    Runs the same checks the git hooks run — the pre-commit hook (whitespace
    fixes, flake8, mypy) and a simulation of the pre-push hook — so you can
    verify your changes will pass before committing or pushing. Reports the
    combined pass/fail in the exit code.

    Aliased as `hooks`.
    """
    console.print('[primary]Running pre-commit hooks...[/primary]')
    run_cmdline(config.root_dir.joinpath('.git/hooks/pre-commit').as_posix())
    console.print('[primary]Running simulated pre-push hooks...[/primary]')
    cmd_line = ('echo "refs/heads/master $(git rev-parse HEAD) refs/heads/master $(git rev-parse origin/master)" | '
                f'{config.root_dir.joinpath(".git/hooks/pre-push").as_posix()}')
    result = run_cmdline(cmd_line)
    return result


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
