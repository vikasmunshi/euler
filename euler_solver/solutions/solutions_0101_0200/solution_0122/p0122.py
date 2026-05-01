#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 122: Efficient Exponentiation.

Problem Statement:
    The most naive way of computing n^15 requires fourteen multiplications:
    n * n * ... * n = n^15.

    But using a "binary" method you can compute it in six multiplications:
    n * n = n^2
    n^2 * n^2 = n^4
    n^4 * n^4 = n^8
    n^8 * n^4 = n^12
    n^12 * n^2 = n^14
    n^14 * n = n^15

    However it is yet possible to compute it in only five multiplications:
    n * n = n^2
    n^2 * n = n^3
    n^3 * n^3 = n^6
    n^6 * n^6 = n^12
    n^12 * n^3 = n^15

    We shall define m(k) to be the minimum number of multiplications to compute n^k;
    for example m(15) = 5.

    Find sum_{k = 1}^{200} m(k).

URL: https://projecteuler.net/problem=122
"""
from typing import Any

euler_problem: int = 122
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 15}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 200}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 400}, 'answer': None},
]
encrypted: str = (
    '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'
    '4gopCDjK/xb0JN3x'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
