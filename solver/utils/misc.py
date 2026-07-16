#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `problems` and `manage-config` commands."""
from typing import Literal

__all__ = ['manage_config']

from solver.config import config, ExitCodes
from solver.core.problems import Problem, problems as problem_set
from solver.shell import register, console


@register(requires='reader',
          help_text='Show list of problems ([accent.dim]all[/accent.dim]|solved|unsolved).')
def problems(which: Literal['all', 'solved', 'unsolved'] = 'all') -> int:
    """Print a list of problems and their count.

    Args:
        which:  Which set to list — 'all' (default) every known problem,
                'solved' the problems with a recorded answer, or 'unsolved'
                those without. Mirrors the `{problems}` / `{solved}` /
                `{unsolved}` shell variables.
    """
    if which == 'all':
        collection: list[Problem] = problem_set.problems_list
    elif which == 'solved':
        collection = problem_set.solved_problems
    elif which == 'unsolved':
        collection = problem_set.unsolved_problems
    else:
        raise ValueError(f'invalid problem list: {which}')
    for problem in collection:
        console.print(f'[accent.dim]{problem}[/accent.dim]')
    console.print(f'[accent]num {which} problems = {len(collection)}[/accent]')
    return 0


@register(requires='admin', help_text='Manage configuration settings.')
def manage_config(
        param: Literal['all', 'timeout_multiple', 'timeout_single', 'ecb_usd_rate'] = 'all',
        value: float | int | None = None, /,
) -> int:
    """Show or update a managed configuration setting.

    The managed settings persist to `solver/config.json` and override the
    defaults in `config.py`: `timeout_single` / `timeout_multiple` (solution
    timeouts in seconds for a single run and for repeated runs), and
    `ecb_usd_rate` (the rate `costs` uses).

    Args:
        param:  Which setting to act on; 'all' (default) prints every setting.
        value:  When given, the new value to assign to `param` (coerced to the
                setting's type and saved). When omitted, the current value of
                `param` is printed instead.
    """
    config_params: list[str] = ['timeout_multiple', 'timeout_single', 'ecb_usd_rate']
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
