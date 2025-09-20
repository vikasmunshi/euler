#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 370: Geometric Triangles.

Problem Statement:
    Let us define a geometric triangle as an integer sided triangle with sides
    a <= b <= c so that its sides form a geometric progression, i.e. b^2 = a*c

    An example of such a geometric triangle is the triangle with sides
    a = 144, b = 156 and c = 169.

    There are 861805 geometric triangles with perimeter <= 10^6.

    How many geometric triangles exist with perimeter <= 2.5*10^13?

URL: https://projecteuler.net/problem=370
"""
from typing import Any

euler_problem: int = 370
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 25000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
