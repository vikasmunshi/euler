#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 408: Admissible Paths Through a Grid.

Problem Statement:
    Let's call a lattice point (x, y) inadmissible if x, y and x+y are all positive
    perfect squares.
    For example, (9, 16) is inadmissible, while (0, 4), (3, 1) and (9, 4) are not.

    Consider a path from point (x1, y1) to point (x2, y2) using only unit steps north
    or east.
    Let's call such a path admissible if none of its intermediate points are inadmissible.

    Let P(n) be the number of admissible paths from (0, 0) to (n, n).
    It can be verified that P(5) = 252, P(16) = 596994440 and P(1000) mod 1,000,000,007
    = 341920854.

    Find P(10,000,000) mod 1,000,000,007.

URL: https://projecteuler.net/problem=408
"""
from typing import Any

euler_problem: int = 408
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 5}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
