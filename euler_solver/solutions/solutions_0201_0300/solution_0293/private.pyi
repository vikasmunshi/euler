#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 293: Pseudo-Fortunate Numbers.

Problem Statement:
    An even positive integer N is called admissible if it is a power of 2 or
    if its distinct prime factors are consecutive primes.
    The first twelve admissible numbers are 2, 4, 6, 8, 12, 16, 18, 24, 30, 32,
    36, 48.

    If N is admissible, the smallest integer M > 1 such that N+M is prime is
    called the pseudo-Fortunate number for N.

    For example, N = 630 is admissible since it is even and its distinct prime
    factors are the consecutive primes 2, 3, 5 and 7. The next prime after 631
    is 641, hence the pseudo-Fortunate number for 630 is M = 11. The
    pseudo-Fortunate number for 16 is 3.

    Find the sum of all distinct pseudo-Fortunate numbers for admissible
    numbers N less than 10^9.

Solution Approach:
    Generate all admissible even N < max_limit: include powers of 2 and numbers
    whose distinct prime factors form a sequence of consecutive primes (must
    include 2 since N is even). Allow prime powers for each prime in the
    consecutive block while keeping N < max_limit. For each N, find the
    smallest M > 1 with N+M prime by testing successive M (likely small).
    Collect distinct M values and sum them. Key ideas: prime sieving,
    multiplicative generation of constrained factor combinations, primality
    testing for small increments. Expected to be practical with optimized
    prime generation and limits on exponent growth.

Answer: ...
URL: https://projecteuler.net/problem=293
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 293
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}},
    {'category': 'main', 'input': {'max_limit': 1000000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pseudo_fortunate_numbers_p0293_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))