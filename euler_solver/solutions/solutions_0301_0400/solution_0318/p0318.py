#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 318: 2011 Nines.

Problem Statement:
    Consider the real number sqrt(2) + sqrt(3).
    When we calculate the even powers of sqrt(2) + sqrt(3) we get:
    (sqrt(2) + sqrt(3))^2  = 9.898979485566356 ...
    (sqrt(2) + sqrt(3))^4  = 97.98979485566356 ...
    (sqrt(2) + sqrt(3))^6  = 969.998969071069263 ...
    (sqrt(2) + sqrt(3))^8  = 9601.99989585502907 ...
    (sqrt(2) + sqrt(3))^10 = 95049.999989479221 ...
    (sqrt(2) + sqrt(3))^12 = 940897.9999989371855 ...
    (sqrt(2) + sqrt(3))^14 = 9313929.99999989263 ...
    (sqrt(2) + sqrt(3))^16 = 92198401.99999998915 ...
    It looks as if the number of consecutive nines at the beginning of the
    fractional part of these powers is non-decreasing. In fact the fractional
    part of (sqrt(2)+sqrt(3))^{2n} approaches 1 for large n.
    Consider all real numbers of the form sqrt(p) + sqrt(q) with p and q
    positive integers and p < q, such that the fractional part of
    (sqrt(p) + sqrt(q))^{2n} approaches 1 for large n.
    Let C(p,q,n) be the number of consecutive nines at the beginning of the
    fractional part of (sqrt(p) + sqrt(q))^{2n}.
    Let N(p,q) be the minimal value of n such that C(p,q,n) >= 2011.
    Find sum_{p+q <= 2011} N(p,q).

URL: https://projecteuler.net/problem=318
"""
from typing import Any

euler_problem: int = 318
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_sum': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_sum': 2011}, 'answer': None},
    {'category': 'extra', 'input': {'max_sum': 10000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
