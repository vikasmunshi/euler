#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 725: Digit Sum Numbers.

Problem Statement:
    A number where one digit is the sum of the other digits is called a digit sum
    number or DS-number for short. For example, 352, 3003 and 32812 are DS-numbers.

    We define S(n) to be the sum of all DS-numbers of n digits or less.

    You are given S(3) = 63270 and S(7) = 85499991450.

    Find S(2020). Give your answer modulo 10^16.

URL: https://projecteuler.net/problem=725
"""
from typing import Any

euler_problem: int = 725
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digits': 3}, 'answer': None},
    {'category': 'main', 'input': {'max_digits': 2020}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
