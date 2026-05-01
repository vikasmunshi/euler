#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 218: Perfect Right-angled Triangles.

Problem Statement:
    Consider the right angled triangle with sides a=7, b=24 and c=25. The area of
    this triangle is 84, which is divisible by the perfect numbers 6 and 28.
    Moreover it is a primitive right angled triangle as gcd(a,b)=1 and gcd(b,c)=1.
    Also c is a perfect square.

    We will call a right angled triangle perfect if
    - it is a primitive right angled triangle
    - its hypotenuse is a perfect square

    We will call a right angled triangle super-perfect if
    - it is a perfect right angled triangle and
    - its area is a multiple of the perfect numbers 6 and 28

    How many perfect right-angled triangles with c <= 10^16 exist that are not
    super-perfect?

URL: https://projecteuler.net/problem=218
"""
from typing import Any

euler_problem: int = 218
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
