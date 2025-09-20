#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 797: Cyclogenic Polynomials.

Problem Statement:
    A monic polynomial is a single-variable polynomial in which the coefficient of highest
    degree is equal to 1.

    Define F to be the set of all monic polynomials with integer coefficients (including
    the constant polynomial p(x)=1). A polynomial p(x) in F is cyclogenic if there exists
    q(x) in F and a positive integer n such that p(x)q(x) = x^n - 1. If n is the smallest
    such positive integer then p(x) is n-cyclogenic.

    Define P_n(x) to be the sum of all n-cyclogenic polynomials. For example, there exist
    ten 6-cyclogenic polynomials (which divide x^6-1 and no smaller x^k-1):
    x^6-1, x^4+x^3-x-1, x^3+2x^2+2x+1, x^2-x+1,
    x^5+x^4+x^3+x^2+x+1, x^4-x^3+x-1, x^3-2x^2+2x-1,
    x^5-x^4+x^3-x^2+x-1, x^4+x^2+1, x^3+1,
    giving P_6(x) = x^6 + 2x^5 + 3x^4 + 5x^3 + 2x^2 + 5x.

    Also define Q_N(x) = sum_{n=1}^N P_n(x).

    It's given that Q_10(x) = x^10 + 3x^9 + 3x^8 + 7x^7 + 8x^6 + 14x^5 + 11x^4 + 18x^3 +
    12x^2 + 23x and Q_10(2) = 5598.

    Find Q_{10^7}(2). Give your answer modulo 1,000,000,007.

URL: https://projecteuler.net/problem=797
"""
from typing import Any

euler_problem: int = 797
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'N': 10000000, 'x': 2}, 'answer': None},
]
encrypted: str = (
    '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'
    'yPan9Ab8+CChCWp5'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
