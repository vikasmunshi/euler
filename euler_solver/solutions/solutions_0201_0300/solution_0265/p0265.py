#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 265: Binary Circles.

Problem Statement:
    2^N binary digits can be placed in a circle so that all the N-digit
    clockwise subsequences are distinct.

    For N = 3, two such circular arrangements are possible, ignoring
    rotations.

    For the first arrangement, the 3-digit subsequences, in clockwise order,
    are: 000, 001, 010, 101, 011, 111, 110 and 100.

    Each circular arrangement can be encoded as a number by concatenating the
    binary digits starting with the subsequence of all zeros as the most
    significant bits and proceeding clockwise. The two arrangements for
    N = 3 are represented as 00010111_2 = 23 and 00011101_2 = 29.

    Calling S(N) the sum of the unique numeric representations, we have
    S(3) = 23 + 29 = 52.

    Find S(5).

URL: https://projecteuler.net/problem=265
"""
from typing import Any

euler_problem: int = 265
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 3}, 'answer': None},
    {'category': 'main', 'input': {'n': 5}, 'answer': None},
    {'category': 'extra', 'input': {'n': 4}, 'answer': None},
]
encrypted: str = (
    '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'
    'fwJ9H7l3FRA/PAzIswBx1g=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
