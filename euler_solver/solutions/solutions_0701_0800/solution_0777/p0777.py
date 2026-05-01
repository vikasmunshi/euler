#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 777: Lissajous Curves.

Problem Statement:
    For coprime positive integers a and b, let C_{a,b} be the curve defined by:
        x = cos(at)
        y = cos(b(t - π/10))
    where t varies between 0 and 2π.

    For example, C_{2,5} crosses itself at two points (rounded to two decimals):
    (0.31, 0) and (-0.81, 0), yielding d(2, 5) = 0.75.
    Some other given values: d(2,3)=4.5, d(7,4)=39.5, d(7,5)=52, d(10,7)=23.25.

    Define d(a,b) as the sum over all points (x,y) where C_{a,b} crosses itself
    of (x^2 + y^2).

    Let s(m) = sum of d(a,b) for all pairs of coprime integers a,b with 2 ≤ a ≤ m
    and 2 ≤ b ≤ m.

    Given s(10) = 1602.5 and s(100) = 24256505.

    Find s(10^6). Provide the answer in scientific notation rounded to 10 significant
    digits, e.g., s(100) would be 2.425650500e7.

URL: https://projecteuler.net/problem=777
"""
from typing import Any

euler_problem: int = 777
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
