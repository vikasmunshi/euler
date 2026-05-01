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

Answer: 1217
URL: https://projecteuler.net/problem=90
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, List, Tuple

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 90
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': 1217},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_cube_digit_pairs_p0090_s0() -> int:
    squares: List[Tuple[int, int]] = [(int((i_sq := f'{i * i:02d}')[0]), int(i_sq[1])) for i in range(1, 10)]

    def can_display(cube_digits: Tuple[int, ...], digit: int) -> bool:
        return digit in cube_digits or (digit in [6, 9] and (6 in cube_digits or 9 in cube_digits))

    def can_pair_display_all(cube1: Tuple[int, ...], cube2: Tuple[int, ...]) -> bool:
        for first_digit, second_digit in squares:
            if not (can_display(cube1, first_digit) and can_display(cube2, second_digit) or (
                    can_display(cube1, second_digit) and can_display(cube2, first_digit))):
                return False
        return True

    all_cubes: List[Tuple[int, ...]] = list(combinations(range(10), 6))
    cube_count: int = len(all_cubes)
    valid_arrangements: int = 0
    for i in range(cube_count):
        for j in range(i, cube_count):
            if can_pair_display_all(all_cubes[i], all_cubes[j]):
                valid_arrangements += 1
    return valid_arrangements


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
