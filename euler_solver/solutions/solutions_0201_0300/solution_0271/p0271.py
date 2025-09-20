#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 271: Modular Cubes, Part 1.

Problem Statement:
    For a positive number n, define S(n) as the sum of the integers x, for which
    1 < x < n and x^3 ≡ 1 (mod n).

    When n = 91, there are 8 possible values for x, namely:
    9, 16, 22, 29, 53, 74, 79, 81. Thus S(91) = 9+16+22+29+53+74+79+81 = 363.

    Find S(13082761331670030).

URL: https://projecteuler.net/problem=271
"""
from typing import Any

euler_problem: int = 271
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 91}, 'answer': None},
    {'category': 'main', 'input': {'n': 13082761331670030}, 'answer': None},
    {'category': 'extra', 'input': {'n': 1000000007}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
