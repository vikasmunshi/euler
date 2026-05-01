#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 70: Totient Permutation.

Problem Statement:
    Euler's totient function, phi(n) [sometimes called the phi function], is used
    to determine the number of positive numbers less than or equal to n which are
    relatively prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all less than
    nine and relatively prime to nine, phi(9)=6.
    The number 1 is considered to be relatively prime to every positive number, so
    phi(1)=1.

    Interestingly, phi(87109)=79180, and it can be seen that 87109 is a permutation
    of 79180.

    Find the value of n, 1 < n < 10^7, for which phi(n) is a permutation of n and
    the ratio n/phi(n) produces a minimum.

Solution Approach:
    Use number theory and combinatorics to compute phi(n) efficiently. Check
    permutations by digit comparison. Employ a sieve or factorization for phi
    calculations. Search space can be optimized considering properties of n and phi(n).
    Expected complexity involves prime factorization and permutation checks up to 10^7.

Answer: 8319823
URL: https://projecteuler.net/problem=70
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_generator

euler_problem: int = 70
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'limit': 10000000}, 'answer': 8319823},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_totient_permutation_p0070_s0(*, limit: int) -> int:
    min_ratio: float = float('inf')
    min_n: int = 0
    sqrt_n = int(limit ** 0.5)
    min_prime_1, max_prime_1 = (sqrt_n // 2, sqrt_n)
    for prime_1 in (p for p in primes_generator() if p > min_prime_1):
        if prime_1 > max_prime_1:
            break
        min_prime_2, max_prime_2 = (prime_1 + 2, int(limit / prime_1))
        for prime_2 in (p for p in primes_generator() if p > min_prime_2):
            if prime_2 > max_prime_2:
                break
            if (sorted(str((number := (prime_1 * prime_2))))
                    == sorted(str((totient := ((prime_1 - 1) * (prime_2 - 1)))))):
                if (ratio := (number / totient)) < min_ratio:
                    min_ratio, min_n = (ratio, number)
    return min_n


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
