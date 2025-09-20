#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 826: Birds on a Wire.

Problem Statement:
    Consider a wire of length 1 unit between two posts. Every morning n birds land on it
    randomly with every point on the wire equally likely to host a bird. The interval
    from each bird to its closest neighbour is then painted.

    Define F(n) to be the expected length of the wire that is painted. You are given
    F(3) = 0.5.

    Find the average of F(n) where n ranges through all odd prime less than a million.
    Give your answer rounded to 10 places after the decimal point.

URL: https://projecteuler.net/problem=826
"""
from typing import Any

euler_problem: int = 826
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
