#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 81: Path Sum: Two Ways.

Problem Statement:
    In the 5 by 5 matrix below, the minimal path sum from the top left to the bottom
    right, by only moving to the right and down, is indicated in bold red and is equal
    to 2427.

    Find the minimal path sum from the top left to the bottom right by only moving
    right and down in matrix.txt (right click and "Save Link/Target As..."), a 31K text
    file containing an 80 by 80 matrix.

Solution Approach:
    Use dynamic programming to build up the minimal path sums starting from the top-left
    corner, adding only right and down moves. Store intermediate sums in a 2D array.
    This uses O(n^2) time and space for an n x n matrix. Efficiently read and parse the
    input file.

Answer: 427337
URL: https://projecteuler.net/problem=81
"""
from __future__ import annotations

from typing import Any, List, cast

from euler_solver.logger import logger
from euler_solver.maths.c_lib.path_sums import path_sum_two_ways_p0081_s0
from euler_solver.setup import evaluate, register_solution
from euler_solver.utils.load_matrix import load_matrix

euler_problem: int = 81
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'file_url': ''}},
    {'category': 'main', 'input': {'file_url': 'https://projecteuler.net/resources/documents/0081_matrix.txt'}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_path_sum_two_ways_p0081_s0(*, file_url: str) -> int:
    matrix: List[List[int]] = load_matrix(file_url)
    return cast(int, path_sum_two_ways_p0081_s0(matrix))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
