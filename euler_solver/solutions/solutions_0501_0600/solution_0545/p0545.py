#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 545: Faulhaber's Formulas.

Problem Statement:
    The sum of the k-th powers of the first n positive integers can be expressed as a
    polynomial of degree k+1 with rational coefficients, the Faulhaber's Formulas:
    1^k + 2^k + ... + n^k = sum_{i=1}^n i^k = sum_{i=1}^{k+1} a_i n^i = a_1 n + a_2 n^2 +
    ... + a_k n^k + a_{k+1} n^{k+1},
    where a_i's are rational coefficients that can be written as reduced fractions p_i/q_i
    (if a_i = 0, consider q_i = 1).

    For example, 1^4 + 2^4 + ... + n^4 = -1/30 n + 1/3 n^3 + 1/2 n^4 + 1/5 n^5.

    Define D(k) as the value of q_1 for the sum of k-th powers (i.e. the denominator of
    the reduced fraction a_1).
    Define F(m) as the m-th value of k ≥ 1 for which D(k) = 20010.
    Given D(4) = 30 since a_1 = -1/30, D(308) = 20010, F(1) = 308, F(10) = 96404.

    Find F(10^5).

URL: https://projecteuler.net/problem=545
"""
from typing import Any

euler_problem: int = 545
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 1}, 'answer': None},
    {'category': 'main', 'input': {'m': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
