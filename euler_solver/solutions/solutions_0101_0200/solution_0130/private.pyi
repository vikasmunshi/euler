#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 130: Composites with Prime Repunit Property.

Problem Statement:
    A number consisting entirely of ones is called a repunit. We shall define R(k)
    to be a repunit of length k; for example, R(6) = 111111.

    Given that n is a positive integer and gcd(n, 10) = 1, it can be shown that
    there always exists a value, k, for which R(k) is divisible by n, and let
    A(n) be the least such value of k; for example, A(7) = 6 and A(41) = 5.

    You are given that for all primes p > 5 that p - 1 is divisible by A(p).
    For example, when p = 41, A(41) = 5, and 40 is divisible by 5.

    However, there are rare composite values for which this is also true; the
    first five examples being 91, 259, 451, 481, and 703.

    Find the sum of the first twenty-five composite values of n for which
    gcd(n, 10) = 1 and n - 1 is divisible by A(n).

Solution Approach:
    Use number theory: R(k) = (10^k - 1) / 9, and A(n) is the minimal k with
    n | R(k). Compute A(n) by determining the multiplicative order(s) of 10
    modulo appropriate factors and taking lcm across prime-power factors.
    Iterate odd n coprime to 10, skip primes, factor n for efficient order
    computation, and test whether (n - 1) % A(n) == 0. Time depends on
    factorization cost; expect practical runtimes using trial division and
    caching for the first 25 composites.

Answer: ...
URL: https://projecteuler.net/problem=130
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 130
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'count': 5}},
    {'category': 'main', 'input': {'count': 25}},
    {'category': 'extra', 'input': {'count': 100}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_composites_with_prime_repunit_property_p0130_s0(*, count: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))