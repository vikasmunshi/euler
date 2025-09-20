#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 678: Fermat-like Equations.

Problem Statement:
    If a triple of positive integers (a, b, c) satisfies a^2 + b^2 = c^2, it is
    called a Pythagorean triple. No triple (a, b, c) satisfies a^e + b^e = c^e
    when e >= 3 (Fermat's Last Theorem). However, if the exponents of the
    left-hand side and right-hand side differ, this is not true. For example,
    3^3 + 6^3 = 3^5.

    Let a, b, c, e, f be all positive integers, with 0 < a < b, e >= 2, f >= 3,
    and c^f <= N. Let F(N) be the number of (a, b, c, e, f) such that
    a^e + b^e = c^f. You are given F(10^3) = 7, F(10^5) = 53 and F(10^7) = 287.

    Find F(10^18).

URL: https://projecteuler.net/problem=678
"""
from typing import Any

euler_problem: int = 678
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
