#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 147: Rectangles in Cross-hatched Grids.

Problem Statement:
    In a 3 x 2 cross-hatched grid, a total of 37 different rectangles could be
    situated within that grid as indicated in the sketch.

    There are 5 grids smaller than 3 x 2, vertical and horizontal dimensions being
    important: 1 x 1, 2 x 1, 3 x 1, 1 x 2 and 2 x 2. If each of them is
    cross-hatched, the following number of different rectangles could be
    situated within those smaller grids:
    1 x 1 -> 1
    2 x 1 -> 4
    3 x 1 -> 8
    1 x 2 -> 4
    2 x 2 -> 18

    Adding those to the 37 of the 3 x 2 grid gives a total of 72 for 3 x 2 and
    smaller grids.

    How many different rectangles could be situated within 47 x 43 and smaller
    grids?

URL: https://projecteuler.net/problem=147
"""
from typing import Any

euler_problem: int = 147
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_rows': 3, 'max_cols': 2}, 'answer': None},
    {'category': 'main', 'input': {'max_rows': 47, 'max_cols': 43}, 'answer': None},
    {'category': 'extra', 'input': {'max_rows': 100, 'max_cols': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
