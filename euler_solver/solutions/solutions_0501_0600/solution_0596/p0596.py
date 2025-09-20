#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 596: Number of Lattice Points in a Hyperball.

Problem Statement:
    Let T(r) be the number of integer quadruplets x, y, z, t such that
    x^2 + y^2 + z^2 + t^2 <= r^2. In other words, T(r) is the number of
    lattice points in the four-dimensional hyperball of radius r.

    You are given that T(2) = 89, T(5) = 3121, T(100) = 493490641 and
    T(10^4) = 49348022079085897.

    Find T(10^8) mod 1000000007.

URL: https://projecteuler.net/problem=596
"""
from typing import Any

euler_problem: int = 596
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'uNo5TUFnL3Fo4AvIniDuZg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
