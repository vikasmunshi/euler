#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 405: A Rectangular Tiling.

Problem Statement:
    We wish to tile a rectangle whose length is twice its width.
    Let T(0) be the tiling consisting of a single rectangle.
    For n > 0, let T(n) be obtained from T(n-1) by replacing all tiles in
    the following manner:


    The following animation demonstrates the tilings T(n) for n from 0 to 5:


    Let f(n) be the number of points where four tiles meet in T(n).
    For example, f(1) = 0, f(4) = 82 and f(10^9) mod 17^7 = 126897180.

    Find f(10^k) for k = 10^18, give your answer modulo 17^7.

URL: https://projecteuler.net/problem=405
"""
from typing import Any

euler_problem: int = 405
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'k': 1}, 'answer': None},
    {'category': 'extra', 'input': {'k': 10}, 'answer': None},
    {'category': 'extra', 'input': {'k': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'RnizLn5HOKkH/w2Kx+EVfg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
