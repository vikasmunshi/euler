#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 804: Counting Binary Quadratic Representations.

Problem Statement:
    Let g(n) denote the number of ways a positive integer n can be represented
    in the form: x^2 + xy + 41y^2 where x and y are integers. For example,
    g(53) = 4 due to (x,y) in {(-4,1), (-3,-1), (3,1), (4,-1)}.

    Define T(N) = sum_{n=1}^N g(n). You are given T(10^3) = 474 and T(10^6) = 492128.

    Find T(10^16).

URL: https://projecteuler.net/problem=804
"""
from typing import Any

euler_problem: int = 804
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 1000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    '8mLidhSdLV8='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
