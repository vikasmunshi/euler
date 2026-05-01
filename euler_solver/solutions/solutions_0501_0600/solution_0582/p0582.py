#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 582: Nearly Isosceles 120 Degree Triangles.

Problem Statement:
    Let a, b and c be the sides of an integer sided triangle with one angle
    of 120 degrees, a ≤ b ≤ c and b - a ≤ 100.
    Let T(n) be the number of such triangles with c ≤ n.
    T(1000) = 235 and T(10^8) = 1245.
    Find T(10^100).

URL: https://projecteuler.net/problem=582
"""
from typing import Any

euler_problem: int = 582
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZNjSagI6HOY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
