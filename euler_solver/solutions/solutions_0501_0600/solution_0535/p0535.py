#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 535: Fractal Sequence.

Problem Statement:
    Consider the infinite integer sequence S starting with:
    S = 1, 1, 2, 1, 3, 2, 4, 1, 5, 3, 6, 2, 7, 8, 4, 9, 1, 10, 11, 5, ...

    Circle the first occurrence of each integer.
    S = Ⓢ1, 1, Ⓢ2, 1, Ⓢ3, 2, Ⓢ4, 1, Ⓢ5, 3, Ⓢ6, 2, Ⓢ7, Ⓢ8, 4, Ⓢ9, 1, Ⓢ10, Ⓢ11, 5, ...

    The sequence is characterized by the following properties:
        - The circled numbers are consecutive integers starting with 1.
        - Immediately preceding each non-circled number a_i, there are exactly
          floor(sqrt(a_i)) adjacent circled numbers, where floor is the floor function.
        - If we remove all circled numbers, the remaining numbers form a sequence
          identical to S, so S is a fractal sequence.

    Let T(n) be the sum of the first n elements of the sequence.
    You are given T(1) = 1, T(20) = 86, T(10^3) = 364089, and T(10^9) = 498676527978348241.

    Find T(10^18). Give the last 9 digits of your answer.

URL: https://projecteuler.net/problem=535
"""
from typing import Any

euler_problem: int = 535
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 20}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
