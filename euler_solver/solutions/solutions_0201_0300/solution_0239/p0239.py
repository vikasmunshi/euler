#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 239: Twenty-two Foolish Primes.

Problem Statement:
    A set of disks numbered 1 through 100 are placed in a line in random order.

    What is the probability that we have a partial derangement such that
    exactly 22 prime number discs are found away from their natural positions?
    (Any number of non-prime disks may also be found in or out of their natural
    positions.)

    Give your answer rounded to 12 places behind the decimal point in the form
    0.abcdefghijkl.

URL: https://projecteuler.net/problem=239
"""
from typing import Any

euler_problem: int = 239
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
