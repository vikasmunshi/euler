#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 822: Square the Smallest.

Problem Statement:
    A list initially contains the numbers 2, 3, ..., n.
    At each round, the smallest number in the list is replaced by its square.
    If there is more than one such number, then only one of them is replaced.

    For example, below are the first three rounds for n = 5:
    [2, 3, 4, 5] -> (1) [4, 3, 4, 5] -> (2) [4, 9, 4, 5] -> (3) [16, 9, 4, 5].

    Let S(n, m) be the sum of all numbers in the list after m rounds.

    For example, S(5, 3) = 16 + 9 + 4 + 5 = 34.
    Also S(10, 100) ≡ 845339386 (mod 1234567891).

    Find S(10^4, 10^16). Give your answer modulo 1234567891.

Solution Approach:
    The problem involves simulating a sequence where the smallest element is repeatedly squared.
    Key ideas include efficient simulation with priority queues or segment trees.
    Modular arithmetic will be necessary due to large numbers.
    Insight or mathematical pattern-finding could avoid full simulation for large m.
    Expected complexity must handle very large m (10^16) efficiently, possibly with number theory or custom state progression.

Answer: ...
URL: https://projecteuler.net/problem=822
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 822
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5, 'm': 3}},
    {'category': 'main', 'input': {'n': 10000, 'm': 10000000000000000}},
    {'category': 'extra', 'input': {'n': 10, 'm': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_square_the_smallest_p0822_s0(*, n: int, m: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))