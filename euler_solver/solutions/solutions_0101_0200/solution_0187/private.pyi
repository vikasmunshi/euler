#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 187: Semiprimes.

Problem Statement:
    A composite is a number containing at least two prime factors. For example,
    15 = 3 * 5; 9 = 3 * 3; 12 = 2 * 2 * 3.

    There are ten composites below thirty containing precisely two, not
    necessarily distinct, prime factors: 4, 6, 9, 10, 14, 15, 21, 22, 25, 26.

    How many composite integers, n < 10^8, have precisely two, not necessarily
    distinct, prime factors?

Solution Approach:
    Count semiprimes (numbers with exactly two prime factors, counted with
    multiplicity) below a limit. Key ideas: sieve of Eratosthenes to generate
    primes; iterate prime p up to sqrt(limit) and count primes q >= p with
    p * q < limit (use binary search on the primes list). Handle prime
    squares explicitly. Time: sieve O(max_limit log log max_limit) plus
    O(pi(sqrt(max_limit)) log pi(max_limit)) for counting; memory depends on
    sieve size (O(max_limit)).

Answer: ...
URL: https://projecteuler.net/problem=187
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 187
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 30}},
    {'category': 'main', 'input': {'max_limit': 100000000}},
    {'category': 'extra', 'input': {'max_limit': 1000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_semiprimes_p0187_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))