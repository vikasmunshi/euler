#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 785: Symmetric Diophantine Equation.

Problem Statement:
    Consider the following Diophantine equation:
    15  (x^2 + y^2 + z^2) = 34  (xy + yz + zx)
    where x, y and z are positive integers.

    Let S(N) be the sum of all solutions, (x,y,z), of this equation such that,
    1 <= x <= y <= z <= N and gcd(x, y, z) = 1.

    For N = 10^2, there are three such solutions - (1, 7, 16), (8, 9, 39),
    (11, 21, 72). So S(10^2) = 184.

    Find S(10^9).

URL: https://projecteuler.net/problem=785
"""
from typing import Any

euler_problem: int = 785
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
