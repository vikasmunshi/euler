#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 97: Large Non-Mersenne Prime.

Problem Statement:
    The first known prime found to exceed one million digits was discovered in 1999,
    and is a Mersenne prime of the form 2^6972593 - 1; it contains exactly 2098960 digits.
    Subsequently other Mersenne primes, of the form 2^p - 1, have been found which contain
    more digits.

    However, in 2004 there was found a massive non-Mersenne prime which contains 2357207 digits:
    28433 * 2^7830457 + 1.

    Find the last ten digits of this prime number.

Solution Approach:
    Use modular arithmetic to compute (28433 * 2^7830457 + 1) mod 10^10 efficiently.
    Employ fast exponentiation (binary exponentiation) for O(log n) complexity in exponentiation.
    This avoids handling the entire large number outright.

Answer: ...
URL: https://projecteuler.net/problem=97
"""
from __future__ import annotations

from typing import Any

from euler_solver.c_libs import use_wrapped_c_function
from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 97
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'num_digits': 10, 'prime': '28433 \u00d7 2^7830457 + 1'}}
]


@use_wrapped_c_function('p0097')
def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    ...

@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_large_non_mersenne_prime_p0097_s0(*, num_digits: int, prime: str) -> int:
    ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
