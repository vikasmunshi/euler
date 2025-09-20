#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 356: Largest Roots of Cubic Polynomials.

Problem Statement:
    Let a_n be the largest real root of a polynomial g(x) = x^3 - 2^n * x^2 + n.
    For example, a_2 = 3.86619826...
    Find the last eight digits of the sum for i = 1 to 30 of floor(a_i^987654321).
    Note: floor(a) represents the floor function.

URL: https://projecteuler.net/problem=356
"""
from typing import Any

euler_problem: int = 356
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_n': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_n': 30}, 'answer': None},
    {'category': 'extra', 'input': {'max_n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
