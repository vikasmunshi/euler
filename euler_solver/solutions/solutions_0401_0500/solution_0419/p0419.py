#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 419: Look and Say Sequence.

Problem Statement:
    The look and say sequence goes 1, 11, 21, 1211, 111221, 312211, 13112221,
    1113213211, ...
    The sequence starts with 1 and all other members are obtained by describing
    the previous member in terms of consecutive digits.
    It helps to do this out loud:
    1 is 'one one' → 11
    11 is 'two ones' → 21
    21 is 'one two and one one' → 1211
    1211 is 'one one, one two and two ones' → 111221
    111221 is 'three ones, two twos and one one' → 312211
    ...

    Define A(n), B(n) and C(n) as the number of ones, twos and threes in the n'th
    element of the sequence respectively.
    One can verify that A(40) = 31254, B(40) = 20259 and C(40) = 11625.

    Find A(n), B(n) and C(n) for n = 10^12.
    Give your answer modulo 2^30 and separate your values for A, B and C by a comma.
    E.g. for n = 40 the answer would be 31254,20259,11625

URL: https://projecteuler.net/problem=419
"""
from typing import Any

euler_problem: int = 419
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'n': 40}, 'answer': None},
    {'category': 'main', 'input': {'n': 1000000000000}, 'answer': None},
]
encrypted: str = (
    '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'
    'uWVUMQ=='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
