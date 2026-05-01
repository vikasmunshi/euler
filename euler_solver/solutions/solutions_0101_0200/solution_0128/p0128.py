#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 128: Hexagonal Tile Differences.

Problem Statement:
    A hexagonal tile with number 1 is surrounded by a ring of six hexagonal tiles,
    starting at "12 o'clock" and numbering the tiles 2 to 7 in an anti-clockwise
    direction.
    New rings are added in the same fashion, with the next rings being numbered
    8 to 19, 20 to 37, 38 to 61, and so on.
    By finding the difference between tile n and each of its six neighbours we
    shall define PD(n) to be the number of those differences which are prime.
    For example, working clockwise around tile 8 the differences are 12, 29, 11,
    6, 1, and 13. So PD(8) = 3.
    In the same way, the differences around tile 17 are 1, 17, 16, 1, 11, and 10,
    hence PD(17) = 2.
    It can be shown that the maximum value of PD(n) is 3.
    If all of the tiles for which PD(n) = 3 are listed in ascending order to
    form a sequence, the 10th tile would be 271.
    Find the 2000th tile in this sequence.

URL: https://projecteuler.net/problem=128
"""
from typing import Any

euler_problem: int = 128
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 10}, 'answer': None},
    {'category': 'main', 'input': {'n': 2000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 5000}, 'answer': None},
]
encrypted: str = (
    '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'
    'wFj5QFwIJtP5kzWw'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
