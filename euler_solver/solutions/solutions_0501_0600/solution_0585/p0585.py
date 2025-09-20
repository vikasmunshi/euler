#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 585: Nested Square Roots.

Problem Statement:
    Consider the term sqrt(x + sqrt(y) + sqrt(z)) representing a nested square root.
    x, y, and z are positive integers with y and z not perfect squares, so the number
    under the outer root is irrational. However, for some x, y, z combinations, this
    term can be denested into a sum and/or difference of simple square roots of integers.

    Examples:
        sqrt(3 + sqrt(2) + sqrt(2)) = sqrt(2) + 1
        sqrt(8 + sqrt(15) + sqrt(15)) = sqrt(5) + sqrt(3)
        sqrt(20 + sqrt(96) + sqrt(12)) = 3 + sqrt(6) + sqrt(3) - sqrt(2)
        sqrt(28 + sqrt(160) + sqrt(108)) = sqrt(15) + sqrt(6) + sqrt(5) - sqrt(2)

    Let F(n) be the count of different terms sqrt(x + sqrt(y) + sqrt(z)) that can be
    denested into a sum and/or difference of a finite number of square roots, with the
    condition 0 < x <= n, and y and z are not perfect squares.

    Expressions that yield the same value are counted only once.

    Given: F(10)=17, F(15)=46, F(20)=86, F(30)=213, F(100)=2918, F(5000)=11134074.

    Find F(5000000).

URL: https://projecteuler.net/problem=585
"""
from typing import Any

euler_problem: int = 585
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 5000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
