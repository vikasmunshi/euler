#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 808: Reversible Prime Squares.

Problem Statement:
    Both 169 and 961 are the square of a prime. 169 is the reverse of 961.

    We call a number a reversible prime square if:
        1) It is not a palindrome, and
        2) It is the square of a prime, and
        3) Its reverse is also the square of a prime.

    169 and 961 are not palindromes, so both are reversible prime squares.

    Find the sum of the first 50 reversible prime squares.

Solution Approach:
    Use prime generation (e.g. sieve of Eratosthenes) to find primes.
    For each prime p, check if p^2 meets the reversible prime square conditions.
    Efficient reversal and palindrome checks.
    Sum the first 50 such numbers.
    Time complexity should be manageable with prime sieving and lookups.

Answer: ...
URL: https://projecteuler.net/problem=808
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 808
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'count': 50}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_reversible_prime_squares_p0808_s0(*, count: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))