#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 845: Prime Digit Sum.

Problem Statement:
    Let D(n) be the n-th positive integer that has the sum of its digits a prime.
    For example, D(61) = 157 and D(10^8) = 403539364.

    Find D(10^16).

URL: https://projecteuler.net/problem=845
"""
from typing import Any

euler_problem: int = 845
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
