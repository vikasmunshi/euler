#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 926: Total Roundness.

Problem Statement:
    A round number is a number that ends with one or more zeros in a given base.

    Let us define the roundness of a number n in base b as the number of zeros at the
    end of the base b representation of n.
    For example, 20 has roundness 2 in base 2, because the base 2 representation of 20
    is 10100, which ends with 2 zeros.

    Also define R(n), the total roundness of a number n, as the sum of the roundness of
    n in base b for all b > 1.
    For example, 20 has roundness 2 in base 2 and roundness 1 in base 4, 5, 10, 20,
    hence we get R(20)=6.
    You are also given R(10!) = 312.

    Find R(10000000!). Give your answer modulo 10^9 + 7.

URL: https://projecteuler.net/problem=926
"""
from typing import Any

euler_problem: int = 926
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'lXed/+DtDok='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
