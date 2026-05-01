#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 843: Periodic Circles.

Problem Statement:
    This problem involves an iterative procedure that begins with a circle of n ≥ 3
    integers. At each step every number is simultaneously replaced with the absolute
    difference of its two neighbours.

    For any initial values, the procedure eventually becomes periodic.

    Let S(N) be the sum of all possible periods for 3 ≤ n ≤ N. For example, S(6) = 6,
    because the possible periods for 3 ≤ n ≤ 6 are 1, 2, 3. Specifically, n=3 and n=4
    can each have period 1 only, while n=5 can have period 1 or 3, and n=6 can have
    period 1 or 2.

    You are also given S(30) = 20381.

    Find S(100).

URL: https://projecteuler.net/problem=843
"""
from typing import Any

euler_problem: int = 843
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 6}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 200}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZXEo/ErgMpydh3x0NL4coiqccqsr3UmY'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
