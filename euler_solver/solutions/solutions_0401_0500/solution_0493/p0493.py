#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 493: Under the Rainbow.

Problem Statement:
    70 coloured balls are placed in an urn, 10 for each of the seven rainbow colours.

    What is the expected number of distinct colours in 20 randomly picked balls?

    Give your answer with nine digits after the decimal point (a.bcdefghij).

URL: https://projecteuler.net/problem=493
"""
from typing import Any

euler_problem: int = 493
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'GsbzmZilvwXJIpzYFXJFls08soqC/1az'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
