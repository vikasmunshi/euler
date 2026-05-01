#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 876: Triplet Tricks.

Problem Statement:
    Starting with three numbers a, b, c, at each step do one of the three operations:
        change a to 2(b + c) - a;
        change b to 2(c + a) - b;
        change c to 2(a + b) - c;

    Define f(a, b, c) to be the minimum number of steps required for one number to become zero.
    If this is not possible then f(a, b, c) = 0.

    For example, f(6,10,35) = 3:
    (6,10,35) -> (6,10,-3) -> (8,10,-3) -> (8,0,-3).
    However, f(6,10,36) = 0 as no series of operations leads to a zero number.

    Also define F(a, b) = sum_{c=1}^∞ f(a,b,c).
    You are given F(6,10) = 17 and F(36,100) = 179.

    Find the sum of F(6^k, 10^k) for k = 1 to 18.

URL: https://projecteuler.net/problem=876
"""
from typing import Any

euler_problem: int = 876
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_k': 1}, 'answer': None},
    {'category': 'main', 'input': {'max_k': 18}, 'answer': None},
]
encrypted: str = (
    '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'
    '8gStL2HB5lY3qaYvwepd3nSW1c4='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
