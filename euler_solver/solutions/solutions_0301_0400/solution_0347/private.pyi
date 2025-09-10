#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 347: Largest Integer Divisible by Two Primes.

Problem Statement:
    The largest integer <= 100 that is only divisible by both the primes 2
    and 3 is 96, as 96 = 32 * 3 = 2^5 * 3. For two distinct primes p and q
    let M(p, q, N) be the largest positive integer <= N only divisible by
    both p and q and M(p, q, N) = 0 if such a positive integer does not exist.
    E.g. M(2, 3, 100) = 96.
    M(3, 5, 100) = 75 and not 90 because 90 is divisible by 2, 3 and 5.
    Also M(2, 73, 100) = 0 because there does not exist a positive integer <=
    100 that is divisible by both 2 and 73.
    Let S(N) be the sum of all distinct M(p, q, N). S(100) = 2262.
    Find S(10000000).

Solution Approach:
    Use number theory and efficient enumeration of primes (sieve of Eratosthenes).
    Generate all primes up to N, but only consider unordered pairs p < q with
    p * q <= N (otherwise no product with both primes exists).
    For each valid pair compute the largest value p^a * q^b <= N with a,b >= 1
    by iterating powers of the smaller prime and multiplying by powers of the
    larger prime; track the maximum per pair. Use a set to collect distinct
    M(p,q,N) values and sum them. Expected complexity: sieve O(N log log N)
    and pair enumeration bounded by pairs with p*q <= N; optimized Python
    implementation should run in acceptable time for N = 1e7.

Answer: ...
URL: https://projecteuler.net/problem=347
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 347
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 10000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_largest_integer_divisible_by_two_primes_p0347_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))