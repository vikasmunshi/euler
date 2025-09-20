#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 15: Lattice Paths.

Problem Statement:
    Starting in the top left corner of a 2 x 2 grid, and only being able to move
    to the right and down, there are exactly 6 routes to the bottom right corner.

    How many such routes are there through a 20 x 20 grid?

Solution Approach:
    Use combinatorics: the number of lattice paths in an n x n grid equals the
    central binomial coefficient C(2n, n). This can be computed efficiently using
    multiplicative formula or DP with O(n) complexity.

Answer: 137846528820
URL: https://projecteuler.net/problem=15
"""
from __future__ import annotations

from math import factorial
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 15
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'lattice_size': 2}, 'answer': 6},
    {'category': 'main', 'input': {'lattice_size': 20}, 'answer': 137846528820},
    {'category': 'extra', 'input': {'lattice_size': 200},
     'answer': int('1029525001354144329729758803204019867572109253810776482348490'
                   '59575923332372651958598336595518976492951564048597506774120')},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_lattice_paths_p0015_s0(*, lattice_size: int) -> int:
    return factorial(2 * lattice_size) // factorial(lattice_size) ** 2


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
