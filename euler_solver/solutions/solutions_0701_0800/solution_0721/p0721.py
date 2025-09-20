#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 721: High Powers of Irrational Numbers.

Problem Statement:
    Given is the function f(a,n) = floor((ceil(sqrt(a)) + sqrt(a))^n).
    floor(·) denotes the floor function and ceil(·) denotes the ceiling function.
    For example, f(5,2) = 27 and f(5,5) = 3935.

    Define G(n) = sum from a=1 to n of f(a, a^2).
    It is known that G(1000) modulo 999999937 equals 163861845.

    Find G(5 000 000) modulo 999999937.

URL: https://projecteuler.net/problem=721
"""
from typing import Any

euler_problem: int = 721
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'hjJdDzcaF6VlsT4udCJQwQSPCYOq98kP'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
