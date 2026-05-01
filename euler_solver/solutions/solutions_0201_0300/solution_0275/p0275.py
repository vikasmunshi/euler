#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 275: Balanced Sculptures.

Problem Statement:
    Let us define a balanced sculpture of order n as follows:
    A polyomino made up of n + 1 tiles known as the blocks (n tiles)
    and the plinth (remaining tile);
    the plinth has its centre at position (x = 0, y = 0);
    the blocks have y-coordinates greater than zero (so the plinth is the
    unique lowest tile);
    the centre of mass of all the blocks, combined, has x-coordinate equal
    to zero.
    When counting the sculptures, any arrangements which are simply
    reflections about the y-axis, are not counted as distinct. For example,
    the 18 balanced sculptures of order 6 are shown (mirror pairs counted once).
    There are 964 balanced sculptures of order 10 and 360505 of order 15.
    How many balanced sculptures are there of order 18?

URL: https://projecteuler.net/problem=275
"""
from typing import Any

euler_problem: int = 275
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 18}, 'answer': None},
    {'category': 'extra', 'input': {'n': 15}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
