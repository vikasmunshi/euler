#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 896: Divisible Ranges.

Problem Statement:
    A contiguous range of positive integers is called a divisible range if all the
    integers in the range can be arranged in a row such that the n-th term is a
    multiple of n.

    For example, the range [6..9] is a divisible range because we can arrange the
    numbers as 7,6,9,8.
    In fact, it is the 4th divisible range of length 4, the first three being
    [1..4], [2..5], [3..6].

    Find the 36th divisible range of length 36.
    Give as answer the smallest number in the range.

URL: https://projecteuler.net/problem=896
"""
from typing import Any

euler_problem: int = 896
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'length': 36, 'index': 36}, 'answer': None},
]
encrypted: str = (
    '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'
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
