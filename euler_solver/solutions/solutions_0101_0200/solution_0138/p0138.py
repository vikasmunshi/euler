#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 138: Special Isosceles Triangles.

Problem Statement:
    Consider the isosceles triangle with base length b = 16 and legs L = 17.
    By using the Pythagorean theorem it can be seen that the height
    h = sqrt(17^2 - 8^2) = 15, which is one less than the base length.

    With b = 272 and L = 305, we get h = 273, which is one more than the
    base length, and this is the second smallest isosceles triangle with the
    property that h = b ± 1.

    Find sum L for the twelve smallest isosceles triangles for which
    h = b ± 1 and b, L are positive integers.

URL: https://projecteuler.net/problem=138
"""
from typing import Any

euler_problem: int = 138
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 12}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
