#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 146: Investigating a Prime Pattern.

Problem Statement:
    The smallest positive integer n for which the numbers n^2 + 1, n^2 + 3,
    n^2 + 7, n^2 + 9, n^2 + 13, and n^2 + 27 are consecutive primes is 10.
    The sum of all such integers n below one-million is 1242490.

    What is the sum of all such integers n below 150 million?

Solution Approach:
    Use modular sieving and number theory to filter candidate n by small primes.
    For each small prime p, determine n mod p values that make any n^2 + offset
    divisible by p, and exclude those residues (quadratic residue constraints).
    Build a wheel or sieve over the product of small primes to generate candidates.
    For remaining n, perform fast primality tests (deterministic Miller-Rabin)
    on the six values n^2 + offsets. Complexity: sieve cost O(max_limit) with a tiny
    candidate fraction; primality checks proportional to surviving candidates.

Answer: ...
URL: https://projecteuler.net/problem=146
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 146
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 150000000}},
    {'category': 'extra', 'input': {'max_limit': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_investigating_a_prime_pattern_p0146_s0(*, max_limit: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))