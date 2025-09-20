#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 586: Binary Quadratic Form.

Problem Statement:
    The number 209 can be expressed as a^2 + 3ab + b^2 in two distinct ways:
        209 = 8^2 + 3 * 8 * 5 + 5^2
        209 = 13^2 + 3 * 13 * 1 + 1^2

    Let f(n, r) be the number of integers k not exceeding n that can be expressed
    as k = a^2 + 3ab + b^2, with a > b > 0 integers, in exactly r different ways.

    You are given that f(10^5, 4) = 237 and f(10^8, 6) = 59517.

    Find f(10^15, 40).

URL: https://projecteuler.net/problem=586
"""
from typing import Any

euler_problem: int = 586
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100000, 'r': 4}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000, 'r': 40}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000000, 'r': 6}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
