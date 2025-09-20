#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 290: Digital Signature.

Problem Statement:
    How many integers 0 <= n < 10^18 have the property that the sum of the
    digits of n equals the sum of digits of 137n?

URL: https://projecteuler.net/problem=290
"""
from typing import Any

euler_problem: int = 290
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'DquTSlvoaakEoR6O'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
