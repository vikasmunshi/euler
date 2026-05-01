#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 281: Pizza Toppings.

Problem Statement:
    You are given a pizza (perfect circle) that has been cut into m * n equal
    pieces and you want to have exactly one topping on each slice.

    Let f(m, n) denote the number of ways you can have toppings on the pizza
    with m different toppings (m >= 2), using each topping on exactly n
    slices (n >= 1). Reflections are considered distinct, rotations are not.

    Thus, for instance, f(2, 1) = 1, f(2, 2) = f(3, 1) = 2 and f(3, 2) = 16.

    Find the sum of all f(m, n) such that f(m, n) <= 10^15.

URL: https://projecteuler.net/problem=281
"""
from typing import Any

euler_problem: int = 281
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '5y/ZtEEf2+cH8x9nhNzURQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
