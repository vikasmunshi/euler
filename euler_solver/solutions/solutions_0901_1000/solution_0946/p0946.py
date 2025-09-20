#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 946: Continued Fraction Fraction.

Problem Statement:
    Given the representation of a continued fraction
    a_0+ 1/(a_1+1/(a_2+1/(a_3+...))) = [a_0; a_1,a_2,a_3,...]

    α is a real number with continued fraction representation:
    α = [2;1,1,2,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,2,...]
    where the number of 1's between each of the 2's are consecutive prime numbers.

    β is another real number defined as
        β = (2α + 3) / (3α + 2)

    The first ten coefficients of the continued fraction of β are [0; 1, 5, 6, 16, 9, 1, 10, 16, 11]
    with sum 75.

    Find the sum of the first 10^8 coefficients of the continued fraction of β.

URL: https://projecteuler.net/problem=946
"""
from typing import Any

euler_problem: int = 946
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 100000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'VA8yIBT+CcbWjzWgAf8deCnvpFQ='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
