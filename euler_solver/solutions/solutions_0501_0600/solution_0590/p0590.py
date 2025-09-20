#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 590: Sets with a Given Least Common Multiple.

Problem Statement:
    Let H(n) denote the number of sets of positive integers such that the least
    common multiple of the integers in the set equals n.
    E.g.:
    The integers in the following ten sets all have a least common multiple of 6:
    {2,3}, {1,2,3}, {6}, {1,6}, {2,6}, {1,2,6}, {3,6}, {1,3,6}, {2,3,6} and {1,2,3,6}.
    Thus H(6)=10.

    Let L(n) denote the least common multiple of the numbers 1 through n.
    E.g. L(6) is the least common multiple of the numbers 1,2,3,4,5,6 and L(6) equals 60.

    Let HL(n) denote H(L(n)).
    You are given HL(4)=H(12)=44.

    Find HL(50000). Give your answer modulo 10^9.

URL: https://projecteuler.net/problem=590
"""
from typing import Any

euler_problem: int = 590
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 4}, 'answer': None},
    {'category': 'main', 'input': {'n': 50000}, 'answer': None},
]
encrypted: str = (
    '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'
    'esurRhjMo1nnvOhlXX1YRMurxt0='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
