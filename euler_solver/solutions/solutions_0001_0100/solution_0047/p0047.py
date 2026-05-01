#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 47: Distinct Primes Factors.

Problem Statement:
    The first two consecutive numbers to have two distinct prime factors are:
        14 = 2 × 7
        15 = 3 × 5.

    The first three consecutive numbers to have three distinct prime factors are:
        644 = 2^2 × 7 × 23
        645 = 3 × 5 × 43
        646 = 2 × 17 × 19.

    Find the first four consecutive integers to have four distinct prime factors each.
    What is the first of these numbers?

Solution Approach:
    Use number theory and prime factorization techniques. Efficient prime factorization
    methods such as a sieve for smallest prime factors or trial division up to sqrt(n)
    help check the count of distinct prime factors per number. Search for consecutive
    integers meeting the condition. Expected complexity dominated by factorization cost.

Answer: 134043
URL: https://projecteuler.net/problem=47
"""
from __future__ import annotations

from itertools import count
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import prime_factor_count

euler_problem: int = 47
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': 14},
    {'category': 'dev', 'input': {'n': 3}, 'answer': 644},
    {'category': 'main', 'input': {'n': 4}, 'answer': 134043},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_distinct_primes_factors_p0047_s0(*, n: int) -> int:
    return next((number for number in count(2) if not any((prime_factor_count(number + i) != n for i in range(0, n)))))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
