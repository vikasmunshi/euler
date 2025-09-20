#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 714: Duodigits.

Problem Statement:
    We call a natural number a duodigit if its decimal representation uses no
    more than two different digits. For example, 12, 110 and 33333 are duodigits,
    while 102 is not.
    It can be shown that every natural number has duodigit multiples. Let d(n) be
    the smallest (positive) multiple of the number n that happens to be a duodigit.
    For example, d(12)=12, d(102)=1122, d(103)=515, d(290)=11011010 and d(317)=211122.

    Let D(k) = sum of d(n) for n=1 to k. You are given D(110) = 11047, D(150) = 53312,
    and D(500) = 29570988.

    Find D(50000). Give your answer in scientific notation rounded to 13 significant
    digits (12 after the decimal point). For example, if asked for D(500), the answer
    format would be 2.957098800000e7.

URL: https://projecteuler.net/problem=714
"""
from typing import Any

euler_problem: int = 714
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 150}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 50000}, 'answer': None},
    {'category': 'extra', 'input': {'max_limit': 100000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
