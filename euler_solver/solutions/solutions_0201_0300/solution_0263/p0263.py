#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 263: An Engineers' Dream Come True.

Problem Statement:
    Consider the number 6. The divisors of 6 are 1, 2, 3 and 6.
    Every number from 1 up to and including 6 can be written as a sum
    of distinct divisors of 6: 1=1, 2=2, 3=1+2, 4=1+3, 5=2+3, 6=6.
    A number n is called a practical number if every number from 1 up to
    and including n can be expressed as a sum of distinct divisors of n.

    A pair of consecutive prime numbers with a difference of six is called
    a sexy pair. The first sexy pair is (23, 29).

    A triple-pair means three consecutive sexy prime pairs such that the
    second member of each pair is the first member of the next pair.

    We shall call a number n such that:
        (n-9, n-3), (n-3, n+3), (n+3, n+9) form a triple-pair, and
        the numbers n-8, n-4, n, n+4 and n+8 are all practical,
    an engineers' paradise.

    Find the sum of the first four engineers' paradises.

URL: https://projecteuler.net/problem=263
"""
from typing import Any

euler_problem: int = 263
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
