#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 768: Chandelier.

Problem Statement:
    A certain type of chandelier contains a circular ring of n evenly spaced candleholders.
    If only one candle is fitted, then the chandelier will be imbalanced. However, if a second
    identical candle is placed in the opposite candleholder (assuming n is even) then perfect
    balance will be achieved and the chandelier will hang level.

    Let f(n,m) be the number of ways of arranging m identical candles in distinct sockets of a
    chandelier with n candleholders such that the chandelier is perfectly balanced.

    For example, f(4, 2) = 2: assuming the chandelier's four candleholders are aligned with the
    compass points, the two valid arrangements are "North & South" and "East & West". Note that
    these are considered to be different arrangements even though they are related by rotation.

    You are given that f(12,4) = 15 and f(36, 6) = 876.

    Find f(360, 20).

URL: https://projecteuler.net/problem=768
"""
from typing import Any

euler_problem: int = 768
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4, 'm': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 360, 'm': 20}, 'answer': None},
    {'category': 'extra', 'input': {'n': 720, 'm': 40}, 'answer': None},
]
encrypted: str = (
    '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'
    'Wpgmszl98zxT9d4P3eSaaI7qP428umxB'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
