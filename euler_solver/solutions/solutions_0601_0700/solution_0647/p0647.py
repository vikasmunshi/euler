#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 647: Linear Transformations of Polygonal Numbers.

Problem Statement:
    It is possible to find positive integers A and B such that given any triangular
    number, T_n, then A*T_n + B is always a triangular number. We define F_3(N) to
    be the sum of (A+B) over all such possible pairs (A,B) with max(A,B) <= N. For
    example F_3(100) = 184.

    Polygonal numbers are generalisations of triangular numbers. Polygonal numbers
    with parameter k we call k-gonal numbers. The formula for the nth k-gonal number
    is 1/2 * n * (n(k - 2) + 4 - k) where n >= 1. For example when k=3 we get 1/2 * n *
    (n+1), the formula for triangular numbers.

    The statement above is true for pentagonal, heptagonal and in fact any k-gonal number
    with k odd. For example when k=5 we get the pentagonal numbers and we can find
    positive integers A and B such that given any pentagonal number, P_n, then A*P_n + B
    is always a pentagonal number. We define F_5(N) to be the sum of (A+B) over all such
    possible pairs (A,B) with max(A,B) <= N.

    Similarly we define F_k(N) for odd k. You are given the sum over all odd k = 3,5,7,...
    of F_k(10^3) equals 14993.

    Find the sum over all odd k = 3,5,7,... of F_k(10^12).

URL: https://projecteuler.net/problem=647
"""
from typing import Any

euler_problem: int = 647
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'R/xtd8futrHEa8kchr8RxJ+FObg='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
