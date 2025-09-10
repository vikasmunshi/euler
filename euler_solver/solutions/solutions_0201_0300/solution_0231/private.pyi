#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 231: Prime Factorisation of Binomial Coefficients.

Problem Statement:
    The binomial coefficient C(10, 3) = 120.
    120 = 2^3 * 3 * 5 = 2 * 2 * 2 * 3 * 5, and 2 + 2 + 2 + 3 + 5 = 14.
    So the sum of the terms in the prime factorisation of C(10, 3) is 14.

    Find the sum of the terms in the prime factorisation of C(20000000, 15000000).

Solution Approach:
    Use p-adic valuations and prime enumeration. The sum of terms equals
    sum_{primes p <= n} p * v_p(C(n,k)), where v_p(C(n,k)) is the exponent of p.
    Use Legendre's formula or the digit-sum identity:
    v_p(C(n,k)) = (s_p(k) + s_p(n-k) - s_p(n)) / (p - 1),
    where s_p(x) is the sum of digits of x in base p. Compute primes up to n
    with a fast sieve and evaluate v_p by repeated division or digit extraction.
    Time: dominated by prime enumeration up to n (roughly O(n / log n) primes)
    and per-prime digit work; memory: O(n) for sieve if using classic sieve.

Answer: ...
URL: https://projecteuler.net/problem=231
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 231
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10, 'k': 3}},
    {'category': 'main', 'input': {'n': 20000000, 'k': 15000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_factorisation_of_binomial_coefficients_p0231_s0(*, n: int, k: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))