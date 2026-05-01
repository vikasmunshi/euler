#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 672: One More One.

Problem Statement:
    Consider the following process that can be applied recursively to any positive integer n:
        if n = 1 do nothing and the process stops,
        if n is divisible by 7 divide it by 7,
        otherwise add 1.

    Define g(n) to be the number of 1's that must be added before the process ends.
    For example:
        125 -> +1 -> 126 -> ÷7 -> 18 -> +1 -> 19 -> +1 -> 20 -> +1 -> 21 -> ÷7 -> 3
         -> +1 -> 4 -> +1 -> 5 -> +1 -> 6 -> +1 -> 7 -> ÷7 -> 1.
    Eight 1's are added so g(125) = 8. Similarly g(1000) = 9 and g(10000) = 21.

    Define S(N) = sum of g(n) for n=1 to N and H(K) = S((7^K - 1)/11).
    You are given H(10) = 690409338.

    Find H(10^9) modulo 1117117717.

URL: https://projecteuler.net/problem=672
"""
from typing import Any

euler_problem: int = 672
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 10}, 'answer': None},
    {'category': 'main', 'input': {'k': 1000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
