#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 435: Polynomials of Fibonacci Numbers.

Problem Statement:
    The Fibonacci numbers {f_n, n >= 0} are defined recursively as f_n = f_{n-1} + f_{n-2}
    with base cases f_0 = 0 and f_1 = 1.

    Define the polynomials {F_n, n >= 0} as F_n(x) = sum from i=0 to n of f_i * x^i.

    For example, F_7(x) = x + x^2 + 2x^3 + 3x^4 + 5x^5 + 8x^6 + 13x^7, and F_7(11) = 268357683.

    Let n = 10^15. Find the sum from x=0 to 100 of F_n(x), and give your answer modulo 1307674368000 (15!).

URL: https://projecteuler.net/problem=435
"""
from typing import Any

euler_problem: int = 435
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 1000000000000000, 'x_max': 100, 'mod': 1307674368000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
