#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 390: Triangles with Non Rational Sides and Integral Area.

Problem Statement:
    Consider the triangle with sides sqrt(5), sqrt(65) and sqrt(68). It can be
    shown that this triangle has area 9.

    S(n) is the sum of the areas of all triangles with sides sqrt(1+b^2),
    sqrt(1+c^2) and sqrt(b^2+c^2) (for positive integers b and c) that have an
    integral area not exceeding n.

    The example triangle has b = 2 and c = 8.

    S(10^6) = 18018206.

    Find S(10^10).

URL: https://projecteuler.net/problem=390
"""
from typing import Any

euler_problem: int = 390
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1000000}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'e+Cyy5KnLr+hxde5JnnD1q8kmHw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
