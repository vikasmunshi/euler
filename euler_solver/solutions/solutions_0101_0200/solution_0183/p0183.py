#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 183: Maximum Product of Parts.

Problem Statement:
    Let N be a positive integer and let N be split into k equal parts, r = N/k,
    so that N = r + r + ... + r.
    Let P be the product of these parts, P = r * r * ... * r = r^k.

    For example, if 11 is split into five equal parts, 11 = 2.2 + 2.2 + 2.2 + 2.2
    + 2.2, then P = 2.2^5 = 51.53632.

    Let M(N) = P_max for a given value of N.

    It turns out that the maximum for N = 11 is found by splitting eleven into
    four equal parts which leads to P_max = (11/4)^4; that is, M(11) = 14641/256
    = 57.19140625, which is a terminating decimal.

    However, for N = 8 the maximum is achieved by splitting it into three equal
    parts, so M(8) = 512/27, which is a non-terminating decimal.

    Let D(N) = N if M(N) is a non-terminating decimal and D(N) = -N if M(N)
    is a terminating decimal.

    For example, sum_{N = 5}^{100} D(N) is 2438.

    Find sum_{N = 5}^{10000} D(N).

URL: https://projecteuler.net/problem=183
"""
from typing import Any

euler_problem: int = 183
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
