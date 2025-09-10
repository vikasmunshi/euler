#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 660: Pandigital Triangles.

Problem Statement:
    We call an integer sided triangle n-pandigital if it contains one angle of 120
    degrees and, when the sides of the triangle are written in base n, together they
    use all n digits of that base exactly once.

    For example, the triangle (217, 248, 403) is 9-pandigital because it contains
    one angle of 120 degrees and the sides written in base 9 are 261_9, 305_9, 487_9
    using each of the 9 digits of that base once.

    Find the sum of the largest sides of all n-pandigital triangles with 9 ≤ n ≤ 18.

Solution Approach:
    Use geometry and number theory to characterize integer triangles with a 120-degree
    angle. Represent side lengths in base n and check pandigital digit usage via counting.
    Iterate n from 9 to 18 and efficiently enumerate candidate triangles. Use hashing or
    bitmasks for digit checks and memoize repeated computations for performance.

Answer: ...
URL: https://projecteuler.net/problem=660
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 660
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_pandigital_triangles_p0660_s0() -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))