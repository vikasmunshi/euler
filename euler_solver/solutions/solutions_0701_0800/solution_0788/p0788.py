#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 788: Dominating Numbers.

Problem Statement:
    A dominating number is a positive integer that has more than half of its digits
    equal.

    For example, 2022 is a dominating number because three of its four digits are
    equal to 2. But 2021 is not a dominating number.

    Let D(N) be how many dominating numbers are less than 10^N.
    For example, D(4) = 603 and D(10) = 21893256.

    Find D(2022). Give your answer modulo 1_000_000_007.

URL: https://projecteuler.net/problem=788
"""
from typing import Any

euler_problem: int = 788
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 2022}, 'answer': None},
    {'category': 'extra', 'input': {'n': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
    'uGh6wqKx6LIT52arcm+NIw=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
