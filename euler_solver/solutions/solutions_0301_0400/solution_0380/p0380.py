#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 380: Amazing Mazes!

Problem Statement:
    An m x n maze is an m x n rectangular grid with walls placed between
    grid cells such that there is exactly one path from the top-left
    square to any other square. The following are examples of a 9 x 12
    maze and a 15 x 20 maze.

    Let C(m, n) be the number of distinct m x n mazes. Mazes which can
    be formed by rotation and reflection from another maze are considered
    distinct.

    It can be verified that C(1,1) = 1, C(2,2) = 4, C(3,4) = 2415, and
    C(9,12) = 2.5720e46 (in scientific notation rounded to 5 significant
    digits). Find C(100,500) and write your answer in scientific
    notation rounded to 5 significant digits.

    When giving your answer, use a lowercase e to separate mantissa and
    exponent. E.g. if the answer is 1234567891011 then the answer format
    would be 1.2346e12.

URL: https://projecteuler.net/problem=380
"""
from typing import Any

euler_problem: int = 380
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 3, 'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'m': 100, 'n': 500}, 'answer': None},
    {'category': 'extra', 'input': {'m': 9, 'n': 12}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
