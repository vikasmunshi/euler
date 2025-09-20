#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 67: Maximum Path Sum II.

Problem Statement:
    By starting at the top of the triangle below and moving to adjacent numbers
    on the row below, the maximum total from top to bottom is 23.

        3
        7 4
        2 4 6
        8 5 9 3

    That is, 3 + 7 + 4 + 9 = 23.

    Find the maximum total from top to bottom in triangle.txt (right click and
    'Save Link/Target As...'), a 15K text file containing a triangle with
    one-hundred rows.

    NOTE: This is a much more difficult version of Problem 18. It is not possible
    to try every route to solve this problem, as there are 2^99 altogether! If
    you could check one trillion (10^12) routes every second it would take over
    twenty billion years to check them all. There is an efficient algorithm to
    solve it. ;o)

Solution Approach:
    Use dynamic programming from the bottom up to compute max path sums. Move
    upward, at each step summing the current value with the max of the two
    adjacent numbers below. The complexity is O(n^2) for n rows, feasible for
    100 rows. File reading and triangle parsing are needed.

Answer: 7273
URL: https://projecteuler.net/problem=67
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, List

from euler_solver.framework import evaluate, get_text_file, logger, register_solution

euler_problem: int = 67
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0067_triangle.txt'},
     'answer': 7273},
]


def text2triangle(text: str) -> List[List[int]]:
    return [[int(num) for num in line.split(' ')] for line in text.splitlines() if line != '']


def max_path_sum_triangle(triangle: List[List[int]]) -> int:
    triangle = deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_maximum_path_sum_ii_p0067_s0(*, file_url: str) -> int:
    triangle_str: str = get_text_file(file_url)
    triangle: List[List[int]] = text2triangle(triangle_str)
    return max_path_sum_triangle(triangle)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
