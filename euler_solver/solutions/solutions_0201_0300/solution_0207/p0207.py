#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 207: Integer Partition Equations.

Problem Statement:
    For some positive integers k there exists an integer partition of the form
    4^t = 2^t + k, where 4^t, 2^t and k are all positive integers and t is a
    real number.
    The first two such partitions are 4^1 = 2^1 + 2 and
    4^{1.5849625...} = 2^{1.5849625...} + 6.
    Partitions where t is also an integer are called perfect.
    For any m >= 1 let P(m) be the proportion of such partitions that are
    perfect with k <= m. Thus P(6) = 1/2.
    In the following table some values of P(m) are listed:
    P(5) = 1/1
    P(10) = 1/2
    P(15) = 2/3
    P(20) = 1/2
    P(25) = 1/2
    P(30) = 2/5
    ...
    P(180) = 1/4
    P(185) = 3/13
    Find the smallest m for which P(m) < 1/12345.

URL: https://projecteuler.net/problem=207
"""
from typing import Any

euler_problem: int = 207
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'threshold_denom': 2}, 'answer': None},
    {'category': 'main', 'input': {'threshold_denom': 12345}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
