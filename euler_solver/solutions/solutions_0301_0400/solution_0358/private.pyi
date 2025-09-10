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

Solution Approach:
    Represent the unknown cyclic number N of length n and use the rotation
    property to derive modular congruences: multiplying by k corresponds to a
    rotation, so k*N ≡ 10^r * N (mod 10^n - 1) for some rotation r.
    Use number theory: multiplicative orders, properties of full-reptend primes
    and modular arithmetic to enumerate candidate lengths n and rotations.
    Impose the known leftmost and rightmost digit constraints as congruences
    and solve (CRT / modular solving) for the middle digits. Expected to search
    over feasible n values and solve using integer modular methods.

Answer: ...
URL: https://projecteuler.net/problem=358
"""
from __future__ import annotations

from typing import Any

from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 358
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {}}
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_cyclic_numbers_p0358_s0() -> int: ...


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))