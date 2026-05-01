#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 409: Nim Extreme.

Problem Statement:
    Let n be a positive integer. Consider nim positions where:
        - There are n non-empty piles.
        - Each pile has size less than 2^n.
        - No two piles have the same size.

    Let W(n) be the number of winning nim positions satisfying the above conditions
    (a position is winning if the first player has a winning strategy). For example,
    W(1) = 1, W(2) = 6, W(3) = 168, W(5) = 19764360 and W(100) mod 1,000,000,007 = 384777056.

    Find W(10,000,000) mod 1,000,000,007.

URL: https://projecteuler.net/problem=409
"""
from typing import Any

euler_problem: int = 409
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '2SNGqhv3E3ur+ltHdxOPIEIhdZY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
