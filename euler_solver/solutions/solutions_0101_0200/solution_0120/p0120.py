#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 120: Square Remainders.

Problem Statement:
    Let r be the remainder when (a - 1)^n + (a + 1)^n is divided by a^2.
    For example, if a = 7 and n = 3, then r = 42: 6^3 + 8^3 = 728 = 42 (mod 49).
    And as n varies, so too will r, but for a = 7 it turns out that r_max = 42.
    For 3 <= a <= 1000, find the sum of r_max.

URL: https://projecteuler.net/problem=120
"""
from typing import Any

euler_problem: int = 120
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
