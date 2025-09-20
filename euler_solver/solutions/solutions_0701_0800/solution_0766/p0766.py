#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 766: Sliding Block Puzzle.

Problem Statement:
    A sliding block puzzle is a puzzle where pieces are confined to a grid and by
    sliding the pieces a final configuration is reached. In this problem the pieces
    can only be slid in multiples of one unit in the directions up, down, left, right.

    A reachable configuration is any arrangement of the pieces that can be achieved
    by sliding the pieces from the initial configuration.

    Two configurations are identical if the same shape pieces occupy the same position
    in the grid. So in the example given in the problem the red squares are
    indistinguishable. For that example the number of reachable configurations is 208.

    Find the number of reachable configurations for the puzzle below. Note that the
    red L-shaped pieces are considered different from the green L-shaped pieces.

URL: https://projecteuler.net/problem=766
"""
from typing import Any

euler_problem: int = 766
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
