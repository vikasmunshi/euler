#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 498: Remainder of Polynomial Division.

Problem Statement:
    For positive integers n and m, we define two polynomials F_n(x) = x^n and G_m(x) = (x-1)^m.
    We also define a polynomial R_{n,m}(x) as the remainder of the division of F_n(x) by G_m(x).
    For example, R_{6,3}(x) = 15x^2 - 24x + 10.

    Let C(n, m, d) be the absolute value of the coefficient of the d-th degree term of
    R_{n,m}(x). We can verify that C(6, 3, 1) = 24 and C(100, 10, 4) = 227197811615775.

    Find C(10^13, 10^12, 10^4) modulo 999999937.

URL: https://projecteuler.net/problem=498
"""
from typing import Any

euler_problem: int = 498
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6, 'm': 3, 'd': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000000, 'm': 1000000000000, 'd': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
    'CV8er0bp4N4tRgAM'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
