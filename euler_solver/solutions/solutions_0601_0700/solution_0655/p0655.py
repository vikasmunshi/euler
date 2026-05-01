#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 655: Divisible Palindromes.

Problem Statement:
    The numbers 545, 5995 and 15151 are the three smallest palindromes divisible
    by 109. There are nine palindromes less than 100000 which are divisible by 109.

    How many palindromes less than 10^32 are divisible by 10000019?

URL: https://projecteuler.net/problem=655
"""
from typing import Any

euler_problem: int = 655
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100000.0, 'divisor': 109}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1e+32, 'divisor': 10000019}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
