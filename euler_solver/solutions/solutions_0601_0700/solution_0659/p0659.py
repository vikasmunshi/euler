#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 659: Largest Prime.

Problem Statement:
    Consider the sequence  n^2+3 with n ≥ 1.
    If we write down the first terms of this sequence we get:
    4, 7, 12, 19, 28, 39, 52, 67, 84, 103, 124, 147, 172, 199, 228, 259, 292,
    327, 364, ...
    We see that the terms for n=6 and n=7 (39 and 52) are both divisible by 13.
    In fact 13 is the largest prime dividing any two successive terms of this sequence.

    Let P(k) be the largest prime that divides any two successive terms of the sequence
    n^2+k^2.

    Find the last 18 digits of sum_{k=1}^{10000000} P(k).

URL: https://projecteuler.net/problem=659
"""
from typing import Any

euler_problem: int = 659
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'ZirX0zEyVrw='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
