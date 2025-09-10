#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 274: Divisibility Multipliers.

Problem Statement:
    For each integer p > 1 coprime to 10 there is a positive divisibility
    multiplier m < p which preserves divisibility by p for the following
    function on any positive integer, n:

    f(n) = (all but the last digit of n) + (the last digit of n) * m.

    That is, if m is the divisibility multiplier for p, then f(n) is
    divisible by p if and only if n is divisible by p.

    When n is much larger than p, f(n) will be less than n and repeated
    application of f provides a multiplicative divisibility test for p.

    For example, the divisibility multiplier for 113 is 34.

    f(76275) = 7627 + 5 * 34 = 7797: 76275 and 7797 are both divisible by 113.
    f(12345) = 1234 + 5 * 34 = 1404: 12345 and 1404 are both not divisible
    by 113.

    The sum of the divisibility multipliers for the primes that are coprime
    to 10 and less than 1000 is 39517. What is the sum of the divisibility
    multipliers for the primes that are coprime to 10 and less than 10^7?

Solution Approach:
    Observe for n = 10*q + r that f(n) = q + r*m. Working mod p we require
    10*q + r ≡ 0 (mod p) ⇔ q + r*m ≡ 0 (mod p) for all q,r, which yields
    10*m ≡ 1 (mod p). Thus m is the modular inverse of 10 modulo p.
    For primes p not dividing 10 the inverse exists; compute m as the
    smallest positive residue of 10^{-1} mod p.

    Efficient plan:
    - Sieve primes up to max_limit (exclude 2 and 5).
    - For each prime p compute m = pow(10, p-2, p) or use extended gcd.
    - Sum m for all such primes.
    Complexity: sieve O(N log log N) time, overall O(pi(N)) modular ops.
    Space: O(N) for the sieve; expected to run within a few minutes for 1e7.

Answer: ...
URL: https://projecteuler.net/problem=274
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 274
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 10000000}},
    {'category': 'extra', 'input': {'max_limit': 100000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_divisibility_multipliers_p0274_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))