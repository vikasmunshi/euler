#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 123: Prime Square Remainders.

Problem Statement:
    Let p_n be the nth prime: 2, 3, 5, 7, 11, ..., and let r be the remainder
    when (p_n - 1)^n + (p_n + 1)^n is divided by p_n^2.

    For example, when n = 3, p_3 = 5, and 4^3 + 6^3 = 280 ≡ 5 mod 25.

    The least value of n for which the remainder first exceeds 10^9 is 7037.

    Find the least value of n for which the remainder first exceeds 10^10.

Solution Approach:
    Use binomial expansion and modular arithmetic to reduce the expression mod p^2.
    Show that r = 2 for even n, and for odd n the sum satisfies r ≡ 2 n p (mod p^2).
    Hence only odd n need to be tested; r can be computed as p * (2 n mod p).
    Generate primes efficiently (sieve) up to the required range and test odd n in order.
    Use the approximation p_n ~ n log n to set an upper bound and iterate until threshold.
    Expected complexity: sieve dominates, roughly O(N log log N) for primes up to bound.

Answer: ...
URL: https://projecteuler.net/problem=123
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 123
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'threshold': 1000000000}},
    {'category': 'main', 'input': {'threshold': 10000000000}},
    {'category': 'extra', 'input': {'threshold': 100000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_square_remainders_p0123_s0(*, threshold: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))