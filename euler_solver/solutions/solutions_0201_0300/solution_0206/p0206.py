#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 206: Concealed Square.

Problem Statement:
    Find the unique positive integer whose square has the form
    1_2_3_4_5_6_7_8_9_0, where each '_' is a single digit.

URL: https://projecteuler.net/problem=206
"""
from typing import Any

euler_problem: int = 206
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    '+oW6zmfLx5+lwprOppr+0ZS5F8M='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
