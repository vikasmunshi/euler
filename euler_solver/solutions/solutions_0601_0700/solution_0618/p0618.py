#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 618: Numbers with a Given Prime Factor Sum.

Problem Statement:
    Consider the numbers 15, 16 and 18:
    15 = 3 × 5 and 3 + 5 = 8.
    16 = 2 × 2 × 2 × 2 and 2 + 2 + 2 + 2 = 8.
    18 = 2 × 3 × 3 and 2 + 3 + 3 = 8.
    15, 16 and 18 are the only numbers that have 8 as sum of the prime factors
    (counted with multiplicity).

    We define S(k) to be the sum of all numbers n where the sum of the prime
    factors (with multiplicity) of n is k.
    Hence S(8) = 15 + 16 + 18 = 49.
    Other examples: S(1) = 0, S(2) = 2, S(3) = 3, S(5) = 5 + 6 = 11.

    The Fibonacci sequence is F1 = 1, F2 = 1, F3 = 2, F4 = 3, F5 = 5, ...
    Find the last nine digits of the sum from k=2 to 24 of S(Fk).

URL: https://projecteuler.net/problem=618
"""
from typing import Any

euler_problem: int = 618
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
