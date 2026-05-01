#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 416: A Frog's Trip.

Problem Statement:
    A row of n squares contains a frog in the leftmost square. By successive jumps
    the frog goes to the rightmost square and then back to the leftmost square.
    On the outward trip he jumps one, two or three squares to the right, and on the
    homeward trip he jumps to the left in a similar manner. He cannot jump outside
    the squares. He repeats the round-trip travel m times.

    Let F(m, n) be the number of the ways the frog can travel so that at most one
    square remains unvisited.
    For example, F(1, 3) = 4, F(1, 4) = 15, F(1, 5) = 46, F(2, 3) = 16 and
    F(2, 100) mod 10^9 = 429619151.

    Find the last 9 digits of F(10, 10^12).

URL: https://projecteuler.net/problem=416
"""
from typing import Any

euler_problem: int = 416
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'m': 1, 'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'m': 10, 'n': 1000000000000}, 'answer': None},
    {'category': 'extra', 'input': {'m': 2, 'n': 100}, 'answer': None},
]
encrypted: str = (
    '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'
    'vHZ1euMg9pRXlciWKaJ5dPOyNwdI9FseUMgpeA=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
