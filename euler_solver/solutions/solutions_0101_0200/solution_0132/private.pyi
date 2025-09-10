#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 132: Large Repunit Factors.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define
    R(k) to be a repunit of length k.

    For example, R(10) = 1111111111 = 11 * 41 * 271 * 9091, and the sum of these
    prime factors is 9414.

    Find the sum of the first forty prime factors of R(10^9).

Solution Approach:
    Use number theory: R(k) = (10^k - 1) / 9. For a prime p (p != 2,5,3) p divides
    R(k) iff the multiplicative order of 10 modulo p divides k (i.e. 10^k ≡ 1 mod p).
    For k = 10^9 the order must be a divisor of 10^9, so it is of the form
    2^a * 5^b. Enumerate primes p (skipping 2,5), test whether pow(10, k % (p-1),
    p) == 1 and then verify minimal order divides k. Collect the first 40 such
    primes and sum them. Complexity governed by prime enumeration and modular
    exponentiation; memory is minimal.

Answer: ...
URL: https://projecteuler.net/problem=132
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 132
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4, 'repunit_length': 10}},
    {'category': 'main', 'input': {'n': 40, 'repunit_length': 1000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_large_repunit_factors_p0132_s0(*, n: int, repunit_length: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))