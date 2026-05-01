#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 812: Dynamical Polynomials.

Problem Statement:
    A dynamical polynomial is a monic polynomial f(x) with integer coefficients such
    that f(x) divides f(x^2-2).

    For example, f(x) = x^2 - x - 2 is a dynamical polynomial because
    f(x^2-2) = x^4 - 5x^2 + 4 = (x^2 + x - 2) f(x).

    Let S(n) be the number of dynamical polynomials of degree n.
    For example, S(2) = 6, as there are six dynamical polynomials of degree 2:
    x^2 - 4x + 4, x^2 - x - 2, x^2 - 4, x^2 - 1, x^2 + x - 1, x^2 + 2x + 1.

    Also, S(5) = 58 and S(20) = 122087.

    Find S(10 000). Give your answer modulo 998244353.

URL: https://projecteuler.net/problem=812
"""
from typing import Any

euler_problem: int = 812
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
