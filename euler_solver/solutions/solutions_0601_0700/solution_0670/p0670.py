#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 670: Colouring a Strip.

Problem Statement:
    A certain type of tile comes in three different sizes - 1 x 1, 1 x 2, and 1 x 3 - and in four
    different colours: blue, green, red and yellow. There is an unlimited number of tiles available
    in each combination of size and colour.

    These are used to tile a 2 x n rectangle, where n is a positive integer, subject to the following
    conditions:
        - The rectangle must be fully covered by non-overlapping tiles.
        - It is not permitted for four tiles to have their corners meeting at a single point.
        - Adjacent tiles must be of different colours.

    For example, an acceptable tiling of a 2 x 12 rectangle is shown, but another tiling is not
    acceptable because it violates the "no four corners meeting at a point" rule.

    Let F(n) be the number of ways the 2 x n rectangle can be tiled subject to these rules. Reflecting
    horizontally or vertically would give different tilings, so these are counted separately.

    Examples: F(2) = 120, F(5) = 45876, and F(100) ≡ 53275818 modulo 1,000,004,321.

    Find F(10^16) modulo 1,000,004,321.

URL: https://projecteuler.net/problem=670
"""
from typing import Any

euler_problem: int = 670
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 2}, 'answer': None},
    {'category': 'main', 'input': {'n': 10000000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 100000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
