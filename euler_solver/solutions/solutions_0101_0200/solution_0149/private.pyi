#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 149: Maximum-sum Subsequence.

Problem Statement:
    Looking at the table below, it is easy to verify that the maximum possible
    sum of adjacent numbers in any direction (horizontal, vertical, diagonal
    or anti-diagonal) is 16 (= 8 + 7 + 1).

    Now, let us repeat the search, but on a much larger scale:

    First, generate four million pseudo-random numbers using a specific form of
    what is known as a "Lagged Fibonacci Generator":

    For 1 <= k <= 55, s_k = [100003 - 200003 k + 300007 k^3] mod 1000000 - 500000.
    For 56 <= k <= 4000000, s_k = [s_{k-24} + s_{k-55} + 1000000] mod 1000000 - 500000.

    Thus, s_10 = -393027 and s_100 = 86613.

    The terms of s are then arranged in a 2000 x 2000 table, using the first
    2000 numbers to fill the first row, the next 2000 numbers the second row,
    and so on.

    Finally, find the greatest sum of (any number of) adjacent entries in any
    direction (horizontal, vertical, diagonal or anti-diagonal).

Solution Approach:
    Generate the sequence s efficiently using the given lagged Fibonacci rules.
    Fill a size x size grid with the sequence (row-major). For each direction
    (rows, columns, main diagonals, anti-diagonals) extract linear sequences and
    apply Kadane's maximum subarray algorithm to find the best sum on that line.
    Track the global maximum over all directions. Key ideas: sequence generation,
    1D max-subarray (Kadane), scanning all directional lines. Time: O(size^2).
    Space: O(size^2) to store the grid (or O(size^2) time and O(size) extra).

Answer: ...
URL: https://projecteuler.net/problem=149
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 149
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'size': 4}},
    {'category': 'main', 'input': {'size': 2000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_maximum_sum_subsequence_p0149_s0(*, size: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))