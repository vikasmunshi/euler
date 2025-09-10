#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 302: Strong Achilles Numbers.

Problem Statement:
    A positive integer n is powerful if p^2 is a divisor of n for every prime
    factor p in n.

    A positive integer n is a perfect power if n can be expressed as a power of
    another positive integer.

    A positive integer n is an Achilles number if n is powerful but not a perfect
    power. For example, 864 and 1800 are Achilles numbers: 864 = 2^5 * 3^3 and
    1800 = 2^3 * 3^2 * 5^2.

    We shall call a positive integer S a Strong Achilles number if both S and
    phi(S) are Achilles numbers. For example, 864 is a Strong Achilles number:
    phi(864) = 288 = 2^5 * 3^2. However, 1800 isn't a Strong Achilles number
    because: phi(1800) = 480 = 2^5 * 3^1 * 5^1.

    There are 7 Strong Achilles numbers below 10^4 and 656 below 10^8.

    How many Strong Achilles numbers are there below 10^18?

    (phi denotes Euler's totient function.)

Solution Approach:
    Generate powerful numbers n = product p_i^{e_i} with all e_i >= 2 and n <
    limit, and exclude perfect powers by checking gcd(e_i) = 1. Use backtracking
    over increasing primes with exponent bounds from the size limit to prune the
    search space. Compute phi(n) multiplicatively: phi(n) = product p_i^{e_i-1}
    * (p_i-1). Factor the (p_i-1) components as needed and combine with the
    p_i factors to test whether phi(n) is powerful and not a perfect power.
    Key tools: prime sieve, cached factorization of small integers, and fast
    integer factorization for larger cofactors (e.g., Pollard-Rho) if required.
    Expected complexity depends on the combinatorial count of exponent vectors;
    with pruning this is feasible but requires careful implementation and caching.

Answer: ...
URL: https://projecteuler.net/problem=302
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 302
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}},
    {'category': 'extra', 'input': {'max_limit': 100000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_strong_achilles_numbers_p0302_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))