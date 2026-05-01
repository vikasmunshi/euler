#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 422: Sequence of Points on a Hyperbola.

Problem Statement:
    Let H be the hyperbola defined by the equation 12x^2 + 7xy - 12y^2 = 625.

    Next, define X as the point (7, 1). It can be seen that X is in H.

    Now we define a sequence of points in H, {P_i: i ≥ 1}, as:
        P_1 = (13, 61/4).
        P_2 = (-43/6, -4).
        For i > 2, P_i is the unique point in H that is different from P_{i-1} and
        such that line P_iP_{i-1} is parallel to line P_{i-2}X. It can be shown
        that P_i is well-defined, and that its coordinates are always rational.

    You are given that P_3 = (-19/2, -229/24), P_4 = (1267/144, -37/12) and
    P_7 = (17194218091/143327232, 274748766781/1719926784).

    Find P_n for n = 11^14 in the following format:
    If P_n = (a/b, c/d) where the fractions are in lowest terms and denominators
    are positive, then the answer is (a + b + c + d) mod 1,000,000,007.

    For n = 7, the answer would have been: 806236837.

URL: https://projecteuler.net/problem=422
"""
from typing import Any

euler_problem: int = 422
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 379749833583241}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
