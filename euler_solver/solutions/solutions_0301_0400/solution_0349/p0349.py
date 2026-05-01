#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 349: Langton's Ant.

Problem Statement:
    An ant moves on a regular grid of squares that are coloured either black or
    white.
    The ant is always oriented in one of the cardinal directions (left, right,
    up or down) and moves from square to adjacent square according to the
    following rules:
    - if it is on a black square, it flips the colour of the square to white,
      rotates 90 degrees counterclockwise and moves forward one square.
    - if it is on a white square, it flips the colour of the square to black,
      rotates 90 degrees clockwise and moves forward one square.
    Starting with a grid that is entirely white, how many squares are black
    after 10^18 moves of the ant?

URL: https://projecteuler.net/problem=349
"""
from typing import Any

euler_problem: int = 349
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 10}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
