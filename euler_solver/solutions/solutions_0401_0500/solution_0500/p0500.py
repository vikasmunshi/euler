#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 500: Problem 500!!!.

Problem Statement:
    The number of divisors of 120 is 16.
    In fact 120 is the smallest number having 16 divisors.

    Find the smallest number with 2^500500 divisors.
    Give your answer modulo 500500507.

URL: https://projecteuler.net/problem=500
"""
from typing import Any

euler_problem: int = 500
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'exponent': 500500, 'modulus': 500500507}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
