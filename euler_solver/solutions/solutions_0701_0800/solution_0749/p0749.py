#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 749: Near Power Sums.

Problem Statement:
    A positive integer, n, is a near power sum if there exists a positive integer, k,
    such that the sum of the kth powers of the digits in its decimal representation is
    equal to either n+1 or n-1. For example 35 is a near power sum number because
    3^2 + 5^2 = 34.

    Define S(d) to be the sum of all near power sum numbers of d digits or less.
    Then S(2) = 110 and S(6) = 2562701.

    Find S(16).

URL: https://projecteuler.net/problem=749
"""
from typing import Any

euler_problem: int = 749
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digits': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_digits': 16}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
