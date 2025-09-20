#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 884: Removing Cubes.

Problem Statement:
    Starting from a positive integer n, at each step we subtract from n the largest
    perfect cube not exceeding n, until n becomes 0.
    For example, with n = 100 the procedure ends in 4 steps:
    100 -> 100 - 4^3 = 36 -> 36 - 3^3 = 9 -> 9 - 2^3 = 1 -> 1 - 1^3 = 0.
    Let D(n) denote the number of steps of the procedure. Thus D(100) = 4.

    Let S(N) denote the sum of D(n) for all positive integers n strictly less than N.
    For example, S(100) = 512.

    Find S(10^17).

URL: https://projecteuler.net/problem=884
"""
from typing import Any

euler_problem: int = 884
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 100}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 100000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
