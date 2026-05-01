#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 141: Square Progressive Numbers.

Problem Statement:
    A positive integer, n, is divided by d and the quotient and remainder are q
    and r respectively. In addition d, q, and r are consecutive positive integer
    terms in a geometric sequence, but not necessarily in that order.

    For example, 58 divided by 6 has quotient 9 and remainder 4. It can also be
    seen that 4, 6, 9 are consecutive terms in a geometric sequence (common
    ratio 3/2). We will call such numbers, n, progressive.

    Some progressive numbers, such as 9 and 10404 = 102^2, happen to also be
    perfect squares. The sum of all progressive perfect squares below one
    hundred thousand is 124657.

    Find the sum of all progressive perfect squares below one trillion (10^12).

URL: https://projecteuler.net/problem=141
"""
from typing import Any

euler_problem: int = 141
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'E9s43g=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
