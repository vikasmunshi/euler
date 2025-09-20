#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 5: Smallest Multiple.

Problem Statement:
    2520 is the smallest number that can be divided by each of the numbers from 1
    to 10 without any remainder.

    What is the smallest positive number that is evenly divisible by all of the
    numbers from 1 to 20?

Solution Approach:
    Use number theory: find the least common multiple (LCM) of numbers 1 through 20.
    Apply prime factorization or iterative LCM with gcd to combine factors efficiently.
    Time complexity is O(n log n) with efficient gcd.

Answer: 232792560
URL: https://projecteuler.net/problem=5
"""
from __future__ import annotations

from functools import reduce
from math import gcd
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 5
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': 2520},
    {'category': 'main', 'input': {'n': 20}, 'answer': 232792560},
    {'category': 'extra', 'input': {'n': 50}, 'answer': 3099044504245996706400},
    {'category': 'extra', 'input': {'n': 100}, 'answer': 69720375229712477164533808935312303556800},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_smallest_multiple_p0005_s0(*, n: int) -> int:
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
