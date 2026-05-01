#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 830: Binomials and Powers.

Problem Statement:
    Let S(n) = sum from k=0 to n of (C(n,k) * k^n).

    You are given, S(10) = 142469423360.

    Find S(10^18). Submit your answer modulo 83^3 * 89^3 * 97^3.

URL: https://projecteuler.net/problem=830
"""
from typing import Any

euler_problem: int = 830
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    't4ZXBvO77YIEFrTzbW3SeSpGpjLpyxUS/s3WRQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
