#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 321: Swapping Counters.

Problem Statement:
    A horizontal row comprising of 2n + 1 squares has n red counters placed at one
    end and n blue counters at the other end, separated by a single empty square
    in the centre. For example, when n = 3.

    A counter can move from one square to the next (slide) or can jump over
    another counter (hop) as long as the square next to that counter is unoccupied.

    Let M(n) represent the minimum number of moves/actions to completely reverse
    the positions of the coloured counters; that is, move all the red counters
    to the right and all the blue counters to the left.

    It can be verified M(3) = 15, which also happens to be a triangle number.

    If we create a sequence based on the values of n for which M(n) is a
    triangle number then the first five terms would be:
    1, 3, 10, 22, and 63, and their sum would be 99.

    Find the sum of the first forty terms of this sequence.

URL: https://projecteuler.net/problem=321
"""
from typing import Any

euler_problem: int = 321
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'terms': 5}, 'answer': None},
    {'category': 'main', 'input': {'terms': 40}, 'answer': None},
    {'category': 'extra', 'input': {'terms': 100}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
