#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 955: Finding Triangles.

Problem Statement:
    A sequence (a_n)_{n >= 0} starts with a_0 = 3 and for each n >= 0,
    if a_n is a triangle number, then a_{n + 1} = a_n + 1;
    otherwise, a_{n + 1} = 2a_n - a_{n - 1} + 1.

    A triangle number is a number of the form m(m + 1)/2 for some integer m.

    The sequence begins:
    3, 4, 6, 7, 9, 12, 16, 21, 22, 24, 27, 31, 36, 37, 39, 42, ...
    where triangle numbers are marked in the sequence.

    The 10th triangle number in the sequence is a_{2964} = 1439056.
    Find the index n such that a_n is the 70th triangle number in the sequence.

URL: https://projecteuler.net/problem=955
"""
from typing import Any

euler_problem: int = 955
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'k': 10}, 'answer': None},
    {'category': 'main', 'input': {'k': 70}, 'answer': None},
]
encrypted: str = (
    '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'
    '2f/6XKROSg+mhIgQ'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
