#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 333: Special Partitions.

Problem Statement:
    All positive integers can be partitioned so that every term of the
    partition can be expressed as 2^i * 3^j, where i, j >= 0.

    Consider only such partitions where none of the terms divides any of the
    other terms. For example, the partition of 17 = 2 + 6 + 9
    = (2^1 * 3^0 + 2^1 * 3^1 + 2^0 * 3^2) is not valid since 2 divides 6.
    Neither is 17 = 16 + 1 = (2^4 * 3^0 + 2^0 * 3^0) since 1 divides 16.
    The only valid partition of 17 is 8 + 9 = (2^3 * 3^0 + 2^0 * 3^2).

    Many integers have more than one valid partition. The first such integer
    is 11, which has the two partitions:
    11 = 2 + 9 = (2^1 * 3^0 + 2^0 * 3^2)
    11 = 8 + 3 = (2^3 * 3^0 + 2^0 * 3^1)

    Define P(n) as the number of valid partitions of n. For example P(11)=2.

    Consider only prime integers q for which P(q) = 1, such as q = 17.

    The sum of the primes q < 100 with P(q) = 1 equals 233.

    Find the sum of the primes q < 1000000 such that P(q) = 1.

Solution Approach:
    Represent allowed parts as the multiplicative semigroup {2^i * 3^j}. Use
    number theory and combinatorics to characterize when a prime q has a
    unique partition into such parts with no divisibility among parts.
    Precompute primes up to the limit (sieve) and test representability and
    uniqueness efficiently by exploiting the 2-3 exponent lattice and dominance
    (divisibility) relations. Expect time complexity roughly O(N log log N)
    for sieving plus additional per-prime checks bounded by the density of
    2^i*3^j below the prime.

Answer: ...
URL: https://projecteuler.net/problem=333
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 333
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}},
    {'category': 'main', 'input': {'max_limit': 1000000}},
    {'category': 'extra', 'input': {'max_limit': 2000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_special_partitions_p0333_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))