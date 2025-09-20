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

URL: https://projecteuler.net/problem=333
"""
from typing import Any

euler_problem: int = 333
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
