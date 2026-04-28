#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0040/p0040.py :: solve_champernownes_constant_p0040_s0.

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
URL: https://projecteuler.net/problem=40"""
from __future__ import annotations

from functools import reduce


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


def solve(*, i: int) -> int:
    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10 ** i) for i in range(0, i + 1)), 1)


if __name__ == '__main__':
    import sys

    print(solve(i=int(sys.argv[1])))
