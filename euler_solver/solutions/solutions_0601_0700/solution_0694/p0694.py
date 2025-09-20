#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 694: Cube-full Divisors.

Problem Statement:
    A positive integer n is considered cube-full, if for every prime p that divides n,
    so does p^3. Note that 1 is considered cube-full.

    Let s(n) be the function that counts the number of cube-full divisors of n. For example,
    1, 8 and 16 are the three cube-full divisors of 16. Therefore, s(16)=3.

    Let S(n) represent the summatory function of s(n), that is S(n) = sum_{i=1}^n s(i).

    You are given S(16) = 19, S(100) = 126 and S(10000) = 13344.

    Find S(10^18).

URL: https://projecteuler.net/problem=694
"""
from typing import Any

euler_problem: int = 694
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10000}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
