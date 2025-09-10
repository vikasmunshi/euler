#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 864: Square + 1 = Squarefree.

Problem Statement:
    Let C(n) be the number of squarefree integers of the form x^2 + 1 such that
    1 <= x <= n.

    For example, C(10) = 9 and C(1000) = 895.

    Find C(123567101113).

Solution Approach:
    Use number theory and fast factorization to check squarefreeness of x^2 + 1.
    Efficient sieving or inclusion–exclusion combined with prime factorization
    techniques will be needed for large n. Expected complexity requires optimized
    math and possibly analytic number theory insights.

Answer: ...
URL: https://projecteuler.net/problem=864
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 864
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}},
    {'category': 'main', 'input': {'n': 123567101113}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_square_1_squarefree_p0864_s0(*, n: int) -> int: ...

if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))