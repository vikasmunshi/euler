#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 689: Binary Series.

Problem Statement:
    For 0 <= x < 1, define d_i(x) to be the ith digit after the binary point
    of the binary representation of x.
    For example d_2(0.25) = 1, d_i(0.25) = 0 for i != 2.

    Let f(x) = sum from i=1 to infinity of d_i(x) / i^2.

    Let p(a) be the probability that f(x) > a, given that x is uniformly
    distributed between 0 and 1.

    Find p(0.5). Give your answer rounded to 8 digits after the decimal point.

URL: https://projecteuler.net/problem=689
"""
from typing import Any

euler_problem: int = 689
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'a': 0.5}, 'answer': None},
]
encrypted: str = (
    '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'
    'NDkWsaJcltDg02L8V4I4tP7GoYU='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
