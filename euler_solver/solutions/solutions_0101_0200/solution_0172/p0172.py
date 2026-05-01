#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 172: Few Repeated Digits.

Problem Statement:
    How many 18-digit numbers n (without leading zeros) are there such that no
    digit occurs more than three times in n?

URL: https://projecteuler.net/problem=172
"""
from typing import Any

euler_problem: int = 172
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'BzHJWc7oalkbbSIr'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
