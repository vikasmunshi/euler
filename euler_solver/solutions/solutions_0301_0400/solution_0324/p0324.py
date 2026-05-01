#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 324: Building a Tower.

Problem Statement:
    Let f(n) represent the number of ways one can fill a 3 x 3 x n tower with
    blocks of 2 x 1 x 1.
    You're allowed to rotate the blocks in any way you like; however, rotations,
    reflections etc of the tower itself are counted as distinct.

    For example (with q = 100000007):
    f(2) = 229,
    f(4) = 117805,
    f(10) mod q = 96149360,
    f(10^3) mod q = 24806056,
    f(10^6) mod q = 30808124.

    Find f(10^10000) mod 100000007.

URL: https://projecteuler.net/problem=324
"""
from typing import Any

euler_problem: int = 324
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'power': 1, 'mod': 100000007}, 'answer': None},
    {'category': 'main', 'input': {'power': 10000, 'mod': 100000007}, 'answer': None},
    {'category': 'extra', 'input': {'power': 100000, 'mod': 100000007}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
