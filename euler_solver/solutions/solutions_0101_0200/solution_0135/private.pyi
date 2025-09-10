#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 135: Same Differences.

Problem Statement:
    Given the positive integers, x, y, and z, are consecutive terms of an
    arithmetic progression, the least value of the positive integer, n, for
    which the equation, x^2 - y^2 - z^2 = n, has exactly two solutions is
    n = 27:
    34^2 - 27^2 - 20^2 = 12^2 - 9^2 - 6^2 = 27.

    It turns out that n = 1155 is the least value which has exactly ten
    solutions.

    How many values of n less than one million have exactly ten distinct
    solutions?

Solution Approach:
    Parametrize the progression by y (middle term) and d (difference): x=y+d,
    z=y-d. Then n = x^2 - y^2 - z^2 = y(4d - y). This gives n = a*b with
    a=y, b=4d-y, so a>0, b>0 and a+b ≡ 0 (mod 4). Each valid factor pair
    (a,b) with a<b and a+b divisible by 4 corresponds to a solution.
    For all n < limit count such factor pairs: enumerate divisors or use a
    sieve-assisted factorization to count pairs efficiently. Expected
    complexity roughly O(limit log limit) with a sieve; naive divisor
    enumeration is O(limit * sqrt(limit)).

Answer: ...
URL: https://projecteuler.net/problem=135
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 135
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}},
    {'category': 'main', 'input': {'max_limit': 1000000}},
    {'category': 'extra', 'input': {'max_limit': 2000000}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_same_differences_p0135_s0(*, max_limit: int) -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))