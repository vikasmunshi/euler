#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 443: GCD Sequence.

Problem Statement:
    Let g(n) be a sequence defined as follows:
    g(4) = 13,
    g(n) = g(n-1) + gcd(n, g(n-1)) for n > 4.

    The first few values are:
    n:  4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, ...
    g(n): 13, 14, 16, 17, 18, 27, 28, 29, 30, 31, 32, 33, 34, 51, 54, 55, 60, ...

    You are given that g(1 000) = 2524 and g(1 000 000) = 2624152.

    Find g(10^15).

Solution Approach:
    Use number theory and gcd properties to efficiently iterate or identify a pattern.
    Direct simulation is impossible for 10^15, so analyze the sequence behavior or cycles.
    May involve prime factorization and using fast algorithms for gcd-related recurrences.
    Complexity target: O(log n) or better using advanced math insights or pattern recognition.

Answer: ...
URL: https://projecteuler.net/problem=443
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 443
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 1000000000000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_gcd_sequence_p0443_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))