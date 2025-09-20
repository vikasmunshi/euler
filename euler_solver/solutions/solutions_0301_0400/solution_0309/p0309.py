#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 309: Integer Ladders.

Problem Statement:
    In the classic "Crossing Ladders" problem, we are given the lengths x and y
    of two ladders resting on the opposite walls of a narrow, level street.
    We are also given the height h above the street where the two ladders cross
    and we are asked to find the width of the street (w).

    Here we restrict attention to instances where all four variables x, y, h
    and w are positive integers. For example, if x = 70, y = 119 and h = 30
    then w = 56.

    For integer values x, y, h and 0 < x < y < 200 there are exactly five
    triplets (x, y, h) producing integer w: (70, 119, 30), (74, 182, 21),
    (87, 105, 35), (100, 116, 35) and (119, 175, 40).

    For integer values x, y, h and 0 < x < y < 1,000,000 how many triplets
    (x, y, h) produce integer solutions for w?

URL: https://projecteuler.net/problem=309
"""
from typing import Any

euler_problem: int = 309
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_limit': 200}, 'answer': None},
    {'category': 'main', 'input': {'max_limit': 1000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'dueEMeRUxIaO4jP5wGri6u+T6kc='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
