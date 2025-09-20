#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 219: Skew-cost Coding.

Problem Statement:
    Let A and B be bit strings (sequences of 0's and 1's).
    If A is equal to the leftmost length(A) bits of B, then A is said to be a
    prefix of B. For example, 00110 is a prefix of 001101001, but not of 00111
    or 100110.

    A prefix-free code of size n is a collection of n distinct bit strings such
    that no string is a prefix of any other. For example, this is a prefix-
    free code of size 6:
    0000, 0001, 001, 01, 10, 11

    Now suppose that it costs one penny to transmit a '0' bit, but four pence to
    transmit a '1'. Then the total cost of the prefix-free code shown above is
    35 pence, which happens to be the cheapest possible for the skewed pricing
    scheme in question. In short, we write Cost(6) = 35.

    What is Cost(10^9) ?

URL: https://projecteuler.net/problem=219
"""
from typing import Any

euler_problem: int = 219
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 6}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000}, 'answer': None},
    {'category': 'extra', 'input': {'n': 10000000}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
