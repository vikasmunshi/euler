#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 885: Sorted Digits.

Problem Statement:
    For a positive integer d, let f(d) be the number created by sorting the digits of d in
    ascending order, removing any zeros. For example, f(3403) = 334.

    Let S(n) be the sum of f(d) for all positive integers d of n digits or less. You are given
    S(1) = 45 and S(5) = 1543545675.

    Find S(18). Give your answer modulo 1123455689.

URL: https://projecteuler.net/problem=885
"""
from typing import Any

euler_problem: int = 885
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 1}, 'answer': None},
    {'category': 'main', 'input': {'n': 18}, 'answer': None},
    {'category': 'extra', 'input': {'n': 20}, 'answer': None},
]
encrypted: str = (
    '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'
    'irsaKQ7AX4J0LmolgZ5DqA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
