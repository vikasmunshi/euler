#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 823: Factor Shuffle.

Problem Statement:
    A list initially contains the numbers 2, 3, ..., n.
    At each round, every number in the list is divided by its smallest prime factor.
    Then the product of these smallest prime factors is added to the list as a new number.
    Finally, all numbers that become 1 are removed from the list.

    For example, below are the first three rounds for n = 5:
    [2, 3, 4, 5] -> (1) -> [2, 60] -> (2) -> [30, 4] -> (3) -> [15, 2, 4].
    Let S(n, m) be the sum of all numbers in the list after m rounds.
    For example, S(5, 3) = 15 + 2 + 4 = 21.
    Also S(10, 100) = 257.

    Find S(10^4, 10^16). Give your answer modulo 1234567891.

Solution Approach:
    Model the factorization and their transformations using number theory and combinatorics.
    Use prime factorization, efficient smallest prime factor retrieval, and state transitions.
    Handle large rounds (10^16) via optimized mathematical recurrence or matrix exponentiation.
    Use modular arithmetic for final result. Aim for time complexity feasible with precomputation.

Answer: ...
URL: https://projecteuler.net/problem=823
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 823
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'm': 3}},
    {'category': 'main', 'input': {'n': 10000, 'm': 10000000000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_factor_shuffle_p0823_s0(*, n: int, m: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))