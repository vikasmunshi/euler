#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""The `problems` command."""
from typing import Literal

__all__ = ['problems']

from solver.core.problems import Problem, problems as problem_set
from solver.shell import register, console


@register(requires='reader')
def problems(which: Literal['all', 'solved', 'unsolved'] = 'all') -> int:
    """Print a list of problems and their count.

    The set comes from `problems.json`, the state `summary` imports from your Project Euler
    progress page and `mark` updates as you solve — so "solved" means recorded there, not
    merely present on disk.

    Args:
        which: Which set to list — 'all' every known problem, 'solved' those with a
            recorded answer, 'unsolved' those without. Mirrors the `{problems}` /
            `{solved}` / `{unsolved}` shell variables. Defaults to 'all'.
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
