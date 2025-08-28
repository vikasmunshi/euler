#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 90: Cube Digit Pairs.

Problem Statement:
    Each of the six faces on a cube has a different digit (0 to 9) written on it; the same is
    done to a second cube. By placing the two cubes side-by-side in different positions we
    can form a variety of 2-digit numbers.

    For example, the square number 64 could be formed.

    In fact, by carefully choosing the digits on both cubes it is possible to display all of
    the square numbers below one-hundred: 01, 04, 09, 16, 25, 36, 49, 64, and 81.

    For example, one way this can be achieved is by placing {0, 5, 6, 7, 8, 9} on one cube
    and {1, 2, 3, 4, 8, 9} on the other cube.

    However, for this problem we shall allow the 6 or 9 to be turned upside-down so that an
    arrangement like {0, 5, 6, 7, 8, 9} and {1, 2, 3, 4, 6, 7} allows for all nine square
    numbers to be displayed; otherwise it would be impossible to obtain 09.

    In determining a distinct arrangement we are interested in the digits on each cube, not the
    order.

        {1, 2, 3, 4, 5, 6} is equivalent to {3, 6, 4, 1, 2, 5}
        {1, 2, 3, 4, 5, 6} is distinct from {1, 2, 3, 4, 5, 9}

    But because we are allowing 6 and 9 to be reversed, the two distinct sets in the last example
    both represent the extended set {1, 2, 3, 4, 5, 6, 9} for the purpose of forming 2-digit numbers.

    How many distinct arrangements of the two cubes allow for all of the square numbers to be
    displayed?

Solution Approach:
    Use combinatorics to generate all possible 6-digit selections from digits 0 to 9 for each
    cube. Account for the interchangeability of 6 and 9 by treating them as a single flexible
    digit set. Check all pairs of cubes for the ability to represent all required square numbers
    through digit pairs and orientation. Count unique pairs considering combinations without
    order.

Answer: ...
URL: https://projecteuler.net/problem=90
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, List, Tuple

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 90
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_cube_digit_pairs_p0090_s0() -> int:
    ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
