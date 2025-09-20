#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 174: Hollow Square Laminae II.

Problem Statement:
    We shall define a square lamina to be a square outline with a square hole so
    that the shape possesses vertical and horizontal symmetry.

    Given eight tiles it is possible to form a lamina in only one way: 3 x 3
    square with a 1 x 1 hole in the middle. However, using thirty-two tiles it
    is possible to form two distinct laminae.

    If t represents the number of tiles used, we shall say that t = 8 is type
    L(1) and t = 32 is type L(2).

    Let N(n) be the number of t <= 1000000 such that t is type L(n); for
    example, N(15) = 832.

    What is sum_{n = 1}^{10} N(n)?

URL: https://projecteuler.net/problem=174
"""
from typing import Any

euler_problem: int = 174
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 2000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
