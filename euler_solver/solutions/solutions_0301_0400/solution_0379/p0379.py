#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 379: Least Common Multiple Count.

Problem Statement:
    Let f(n) be the number of couples (x, y) with x and y positive integers,
    x <= y and the least common multiple of x and y equal to n.

    Let g be the summatory function of f, i.e.:
    g(n) = sum f(i) for 1 <= i <= n.

    You are given that g(10^6) = 37429395.

    Find g(10^12).

URL: https://projecteuler.net/problem=379
"""
from typing import Any

euler_problem: int = 379
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
