#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 643: 2-Friendly.

Problem Statement:
    Two positive integers a and b are 2-friendly when gcd(a,b) = 2^t, t > 0.
    For example, 24 and 40 are 2-friendly because gcd(24,40) = 8 = 2^3 while
    24 and 36 are not because gcd(24,36) = 12 = 2^2 * 3 not a power of 2.

    Let f(n) be the number of pairs, (p,q), of positive integers with
    1 <= p < q <= n such that p and q are 2-friendly. You are given
    f(10^2) = 1031 and f(10^6) = 321418433 modulo 1,000,000,007.

    Find f(10^11) modulo 1,000,000,007.

Solution Approach:
    Use number theory to count pairs (p, q) with gcd as a pure power of 2.
    Key ideas include gcd factorization, multiplicative functions, and
    efficient summation using sieves or inclusion-exclusion.
    Modular arithmetic is essential to handle large values.
    Expect O(n log n) or better complexity through careful mathematical
    transforms and fast evaluation.

Answer: ...
URL: https://projecteuler.net/problem=643
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 643
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 100000000000}},
    # Extended test case with a smaller but larger than preliminary value
    {'category': 'extra', 'input': {'max_limit': 1000000}},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_2_friendly_p0643_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))