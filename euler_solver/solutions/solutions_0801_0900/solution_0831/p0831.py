#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 831: Triple Product.

Problem Statement:
    Let g(m) be the integer defined by the following double sum of products of binomial
    coefficients:

        sum from j=0 to m of sum from i=0 to j of (-1)^(j-i) * C(m, j) * C(j, i) * C(j+5+6i, j+5).

    You are given that g(10) = 127278262644918.
    Its first (most significant) five digits are 12727.

    Find the first ten digits of g(142857) when written in base 7.

URL: https://projecteuler.net/problem=831
"""
from typing import Any

euler_problem: int = 831
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 10}, 'answer': None},
    {'category': 'main', 'input': {'m': 142857}, 'answer': None},
]
encrypted: str = (
    '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'
    'uhYWd/cZknXAWFZ6rnpQGg=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
