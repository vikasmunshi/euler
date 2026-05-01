#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Euler Problem 40: Champernowne's Constant.

Problem Statement:
    An irrational decimal fraction is created by concatenating the positive integers:
    0.123456789101112131415161718192021...

    It can be seen that the 12th digit of the fractional part is 1.

    If d_n represents the nth digit of the fractional part, find the value of the
    following expression:
    d_1 × d_10 × d_100 × d_1000 × d_10000 × d_100000 × d_1000000

Solution Approach:
    Identify which integer each digit d_n falls into by cumulative counting digit
    lengths for ranges of integers (1-digit, 2-digit, etc.).
    Extract exact digit by indexing into the integer.
    Multiply extracted digits.
    Use math and efficient indexing rather than building the entire fraction.
    Time complexity is O(log n) due to digit range jumps.

Answer: 1470
URL: https://projecteuler.net/problem=40
"""
from __future__ import annotations

from functools import reduce
from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 40
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'i': 1}, 'answer': 1},
    {'category': 'dev', 'input': {'i': 2}, 'answer': 5},
    {'category': 'dev', 'input': {'i': 3}, 'answer': 15},
    {'category': 'dev', 'input': {'i': 4}, 'answer': 105},
    {'category': 'dev', 'input': {'i': 5}, 'answer': 210},
    {'category': 'dev', 'input': {'i': 6}, 'answer': 210},
    {'category': 'main', 'input': {'i': 7}, 'answer': 1470},
    {'category': 'extra', 'input': {'i': 8}, 'answer': 11760},
    {'category': 'extra', 'input': {'i': 9}, 'answer': 11760},
    {'category': 'extra', 'input': {'i': 10}, 'answer': 11760},
    {'category': 'extra', 'input': {'i': 11}, 'answer': 0},
]


def get_nth_digit_champernowne_s_constant(n: int) -> int:
    length_till_num_digits, length_with_num_digits, num_digits = (0, 0, 0)
    while length_with_num_digits < n:
        num_digits += 1
        length_till_num_digits = length_with_num_digits
        length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)
    offset_of_number = n - length_till_num_digits - 1
    digit_in_number = offset_of_number % num_digits
    number = 10 ** (num_digits - 1) + offset_of_number // num_digits
    return int(str(number)[digit_in_number])


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_champernownes_constant_p0040_s0(*, i: int) -> int:
    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10 ** i) for i in range(0, i + 1)), 1)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
