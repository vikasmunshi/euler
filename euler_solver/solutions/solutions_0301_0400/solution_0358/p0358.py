#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 358: Cyclic Numbers.

Problem Statement:
    A cyclic number with n digits has a very interesting property:
    When it is multiplied by 1, 2, 3, 4, ..., n, all the products have
    exactly the same digits, in the same order, but rotated in a circular
    fashion!

    The smallest cyclic number is the 6-digit number 142857:
    142857 x 1 = 142857
    142857 x 2 = 285714
    142857 x 3 = 428571
    142857 x 4 = 571428
    142857 x 5 = 714285
    142857 x 6 = 857142

    The next cyclic number is 0588235294117647 with 16 digits:
    0588235294117647 x 1 = 0588235294117647
    0588235294117647 x 2 = 1176470588235294
    0588235294117647 x 3 = 1764705882352941
    ...
    0588235294117647 x 16 = 9411764705882352

    Note that for cyclic numbers, leading zeros are important.

    There is only one cyclic number for which the eleven leftmost digits are
    00000000137 and the five rightmost digits are 56789 (i.e., it has the form
    00000000137 ... 56789 with an unknown number of digits in the middle).
    Find the sum of all its digits.

URL: https://projecteuler.net/problem=358
"""
from typing import Any

euler_problem: int = 358
framework_version: str = "0.0.1"
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}, 'answer': None},
]
encrypted: str = (
    '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'
    'R1AQGviktmY='
)

if __name__ == '__main__':
    from euler_solver.framework import evaluate, logger
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
