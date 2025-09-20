#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 7: 10 001st Prime.

Problem Statement:
    By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that
    the 6th prime is 13.

    What is the 10 001st prime number?

Solution Approach:
    Use a prime sieving method or a prime checking algorithm to enumerate primes.
    Efficiently find the nth prime by dynamic sieving or probabilistic prime tests.
    Expected complexity depends on prime generation, typically near O(n log n) or better
    with segmented sieve optimizations.

Answer: 104743
URL: https://projecteuler.net/problem=7
"""
from __future__ import annotations

from math import log
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 7
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6}, 'answer': 13},
    {'category': 'main', 'input': {'n': 10001}, 'answer': 104743},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve__10_001st_prime_p0007_s0(*, n: int) -> int:
    if n == 1:
        return 2
    max_expected_value = int(n * log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + 2 * i * j] = 0
            except IndexError:
                break
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
