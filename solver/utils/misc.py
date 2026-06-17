#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `problems`, `manage-config`, and `lock-status` commands."""
from typing import Literal

__all__ = ['manage_config']

from solver.config import config, ExitCodes
from solver.core.problems import Problem, problems as problem_set
from solver.shell import register, console


@register(help_text='Show list of problems ([accent.dim]all[/accent.dim]|solved|unsolved|stale).')
def problems(which: Literal['all', 'solved', 'unsolved', 'stale'] = 'all') -> int:
    """Print a list of problems and their count.

    Args:
        which:  Which set to list — 'all' (default) every known problem,
                'solved' the problems with a recorded answer, 'unsolved' those
                without, or 'stale' those whose notes are older than their
                solution source. Mirrors the `{problems}` / `{solved}` /
                `{unsolved}` / `{stale}` shell variables.
    """
    if which == 'all':
        collection: list[Problem] = problem_set.problems_list
    elif which == 'solved':
        collection = problem_set.solved_problems
    elif which == 'unsolved':
        collection = problem_set.not_solved_problems
    elif which == 'stale':
        collection = problem_set.stale_problems
    else:
        raise ValueError(f'invalid problem list: {which}')
    for problem in collection:
        console.print(f'[accent.dim]{problem}[/accent.dim]')
    console.print(f'[accent]num {which} problems = {len(collection)}[/accent]')
    return 0


@register(help_text='Manage configuration settings.')
def manage_config(
        param: Literal['all', 'server_port', 'timeout_multiple', 'timeout_single', 'usd_to_eur'] = 'all',
        value: float | int | None = None, /,
) -> int:
    """Show or update a managed configuration setting.

    The managed settings persist to `solver/config.json` and override the
    defaults in `config.py`: `server_port` (the web server's port),
    `timeout_single` / `timeout_multiple` (solution timeouts in seconds for a
    single run and for repeated runs), and `usd_to_eur` (the rate `costs` uses).

    Args:
        param:  Which setting to act on; 'all' (default) prints every setting.
        value:  When given, the new value to assign to `param` (coerced to the
                setting's type and saved). When omitted, the current value of
                `param` is printed instead.
    """
    config_params: list[str] = ['server_port', 'timeout_multiple', 'timeout_single', 'usd_to_eur']
    if param == 'all':
        param_len: int = max(len(p) for p in config_params) + 1
        for config_param in config_params:
            console.print(f'[accent.dim]{config_param:<{param_len}}:[/accent.dim] {config[config_param]}')
        return ExitCodes.EXIT_OK
    if param not in config_params:
        console.print(f'[error]unknown config parameter:[/error] {param}')
        return ExitCodes.EXIT_USAGE
    if value is None:
        console.print(f'[accent.dim]{param}:[/accent.dim] {config[param]}')
        return ExitCodes.EXIT_OK
    try:
        setattr(config, param, type(config[param])(value))
        config.dump_managed_config()
        console.print(f'[success]config parameter updated:[/success] {param} = {value}')
        return ExitCodes.EXIT_OK
    except ValueError:
        console.print(f'[error]invalid value `{value}` for config parameter:[/error] {param}')
        return ExitCodes.EXIT_USAGE


@register(help_text='Check and report the workspace lock status.')
def lock_status() -> int:
    """Report whether this shell holds the workspace lock, and who does.

    Only one shell may own `workspace/` at a time. Prints — and reflects in the
    exit code — one of three states (lock-requiring commands, marked §, refuse to
    run in the last one):

    Returns:
        EXIT_OK (0)     : the lock was inherited from a parent process (PID shown).
        EXIT_USAGE (2)  : this shell acquired the lock (PID shown).
        EXIT_ERROR (1)  : the workspace could not be locked.
    """
    from solver.core.lock import lock_state
    if lock_state.inherited:
        console.print(f'[success]Workspace lock inherited from PID {lock_state.pid_of_holder}[/success]')
        return ExitCodes.EXIT_OK
    if lock_state.acquired:
        console.print(f'[warning]Workspace lock acquired by PID {lock_state.pid_of_holder}[/warning]')
        return ExitCodes.EXIT_USAGE
    console.print(f'[error]Workspace is not locked!{lock_state.held_by}[/error]')
    return ExitCodes.EXIT_ERROR
