#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 18: Maximum Path Sum I.

Problem Statement:
    By starting at the top of the triangle below and moving to adjacent numbers on the
    row below, the maximum total from top to bottom is 23.

    3
    7 4
    2 4 6
    8 5 9 3

    That is, 3 + 7 + 4 + 9 = 23.

    Find the maximum total from top to bottom of the triangle below:

    75
    95 64
    17 47 82
    18 35 87 10
    20 04 82 47 65
    19 01 23 75 03 34
    88 02 77 73 07 63 67
    99 65 04 28 06 16 70 92
    41 41 26 56 83 40 80 70 33
    41 48 72 33 47 32 37 16 94 29
    53 71 44 65 25 43 91 52 97 51 14
    70 11 33 28 77 73 17 78 39 68 17 57
    91 71 52 38 17 14 91 43 58 50 27 29 48
    63 66 04 68 89 53 67 30 73 16 69 87 40 31
    04 62 98 27 23 09 70 98 73 93 38 53 60 04 23

    NOTE: As there are only 16384 routes, it is possible to solve this problem by
    trying every route. However, Problem 67 is the same challenge with a triangle
    containing one-hundred rows; it cannot be solved by brute force, and requires a
    clever method!

Solution Approach:
    Use dynamic programming to efficiently compute the maximum path sum from top to
    bottom. Starting from the second-last row, update each element by adding the max
    of the two adjacent numbers below it. Repeat upwards to the top for an O(n^2)
    solution. This uses bottom-up DP and requires O(n^2) time and space.

Answer: ...
URL: https://projecteuler.net/problem=18
"""
from __future__ import annotations

from typing import Any, List

from euler_solver.logger import logger
from euler_solver.maths.graph_traversal import max_path_sum_triangle
from euler_solver.setup import evaluate, register_solution
from euler_solver.utils.text_to_array import text2triangle

euler_problem: int = 18
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'triangle_str': 'TRIANGLE_A'}},
    {'category': 'main', 'input': {'triangle_str': 'TRIANGLE_B'}}
]

TRIANGLE_A = ('3\n'
              '7 4\n'
              '2 4 6\n'
              '8 5 9 3\n')
TRIANGLE_B = ('75\n'
              '95 64\n'
              '17 47 82\n'
              '18 35 87 10\n'
              '20 04 82 47 65\n'
              '19 01 23 75 03 34\n'
              '88 02 77 73 07 63 67\n'
              '99 65 04 28 06 16 70 92\n'
              '41 41 26 56 83 40 80 70 33\n'
              '41 48 72 33 47 32 37 16 94 29\n'
              '53 71 44 65 25 43 91 52 97 51 14\n'
              '70 11 33 28 77 73 17 78 39 68 17 57\n'
              '91 71 52 38 17 14 91 43 58 50 27 29 48\n'
              '63 66 04 68 89 53 67 30 73 16 69 87 40 31\n'
              '04 62 98 27 23 09 70 98 73 93 38 53 60 04 23\n')


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_maximum_path_sum_i_p0018_s0(*, triangle_str: str) -> int:
    ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
