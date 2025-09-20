#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 247: Squares Under a Hyperbola.

Problem Statement:
    Consider the region constrained by 1 <= x and 0 <= y <= 1/x.
    Let S1 be the largest square that can fit under the curve.
    Let S2 be the largest square that fits in the remaining area, and so on.
    Let the index of Sn be the pair (left, below) indicating the number of
    squares to the left of Sn and the number of squares below Sn.
    The diagram shows some such squares labelled by number.
    S2 has one square to its left and none below, so the index of S2 is (1,0).
    It can be seen that the index of S32 is (1,1) as is the index of S50.
    50 is the largest n for which the index of Sn is (1,1).
    What is the largest n for which the index of Sn is (3,3)?

URL: https://projecteuler.net/problem=247
"""
from typing import Any

euler_problem: int = 247
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'left': 1, 'below': 1}, 'answer': None},
    {'category': 'main', 'input': {'left': 3, 'below': 3}, 'answer': None},
    {'category': 'extra', 'input': {'left': 5, 'below': 5}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
