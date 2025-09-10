#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 280: Ant and Seeds.

Problem Statement:
    A laborious ant walks randomly on a 5 x 5 grid. The walk starts from the
    central square. At each step, the ant moves to an adjacent square at
    random, without leaving the grid; thus there are 2, 3 or 4 possible moves
    at each step depending on the ant's position.

    At the start of the walk, a seed is placed on each square of the lower
    row. When the ant isn't carrying a seed and reaches a square of the lower
    row containing a seed, it will start to carry the seed. The ant will drop
    the seed on the first empty square of the upper row it eventually reaches.

    What is the expected number of steps until all seeds have been dropped in
    the top row? Give the answer rounded to 6 decimal places.

Solution Approach:
    Model the process as an absorbing Markov chain over a finite state space.
    Encode a state by (ant_position, carrying_flag, top_row_mask, bottom_mask).
    Write linear equations: for each transient state s, E[s] = 1 + sum P(s->s')E[s'].
    Solve the sparse linear system for expected hitting times to the absorbing
    states (all top squares occupied). Use symmetry reductions if possible.
    Complexity: O(n) memory for sparse representation, solving depends on chosen
    solver; state count is O(25 * 2 * 2^5 * 2^5) in a straightforward encoding.

Answer: ...
URL: https://projecteuler.net/problem=280
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 280
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_ant_and_seeds_p0280_s0() -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))