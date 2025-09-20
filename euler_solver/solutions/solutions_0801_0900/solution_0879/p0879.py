#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 879: Touch-screen Password.

Problem Statement:
    A touch-screen device can be unlocked with a "password" consisting of a sequence
    of two or more distinct spots that the user selects from a rectangular grid of
    spots on the screen. The user enters their sequence by touching the first spot,
    then tracing a straight line segment to the next spot, and so on until the end
    of the sequence. The user's finger remains in contact with the screen throughout,
    and may only move in straight line segments from spot to spot.

    If the finger traces a straight line that passes over an intermediate spot, then
    that is treated as two line segments with the intermediate spot included in the
    password sequence. For example, on a 3x3 grid labelled with digits 1 to 9, tracing
    1-9 is interpreted as 1-5-9.

    Once a spot has been selected it disappears from the screen. Thereafter, the spot
    may not be used as an endpoint of future line segments, and it is ignored by any
    future line segments which happen to pass through it. For example, tracing 1-9-3-7
    (which crosses the 5 spot twice) will give the password 1-5-9-6-3-7.

    There are 389488 different passwords that can be formed on a 3 x 3 grid.

    Find the number of different passwords that can be formed on a 4 x 4 grid.

URL: https://projecteuler.net/problem=879
"""
from typing import Any

euler_problem: int = 879
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'grid_size': 4}, 'answer': None},
]
encrypted: str = (
    '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'
    'kFDuKAtHT7w='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
