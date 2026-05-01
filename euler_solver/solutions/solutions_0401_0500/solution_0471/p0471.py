#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 471: Triangle Inscribed in Ellipse.

Problem Statement:
    The triangle ABC is inscribed in an ellipse with equation
    x^2/a^2 + y^2/b^2 = 1, where 0 < 2b < a, and a and b are integers.

    Let r(a, b) be the radius of the incircle of triangle ABC when the
    incircle has center (2b, 0) and A has coordinates (a/2, (sqrt(3)/2)*b).

    Examples: r(3,1) = 0.5, r(6,2) = 1, r(12,3) = 2.

    Define G(n) as the sum from a=3 to n of the sums from b=1 to floor((a-1)/2)
    of r(a, b).

    You are given G(10) = 20.59722222 and G(100) = 19223.60980
    (both rounded to 10 significant digits).

    Find G(10^11).

    Provide your answer in scientific notation rounded to 10 significant digits,
    using lowercase 'e' to separate the mantissa and exponent.

    For example, for G(10) the answer would be 2.059722222e1.

URL: https://projecteuler.net/problem=471
"""
from typing import Any

euler_problem: int = 471
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '2nSWZw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
