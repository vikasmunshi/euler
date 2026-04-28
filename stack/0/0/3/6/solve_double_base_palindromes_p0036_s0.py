#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0036/p0036.py :: solve_double_base_palindromes_p0036_s0.

Project Euler Problem 36: Double-base Palindromes.

Problem Statement:
    The decimal number, 585 = 1001001001_2 (binary), is palindromic in both bases.

    Find the sum of all numbers, less than one million, which are palindromic in
    base 10 and base 2.

    (Please note that the palindromic number, in either base, may not include leading
    zeros.)

Solution Approach:
    Check each number less than one million for palindrome property in decimal and
    binary. Efficient palindrome checks can be done by string reversal. Sum all
    qualifying numbers. Time complexity primarily O(N log N) for conversion and checks.

Answer: 872187
URL: https://projecteuler.net/problem=36"""
from __future__ import annotations

from typing import Generator


def generate_decimal_palindromes(max_digits: int) -> Generator[int, None, None]:
    for digit in range(1, 10):
        yield digit
    for digits in range(1, 10 ** (max_digits // 2)):
        digits_str = str(digits)
        digits_rev = digits_str[::-1]
        num_digits = len(digits_str)
        yield int(digits_str + digits_rev)
        if 2 * num_digits < max_digits:
            for mid_digit in '0123456789':
                yield int(digits_str + mid_digit + digits_rev)


def solve(*, max_digits: int) -> int:
    return sum((number for number in generate_decimal_palindromes(max_digits) if
                number == int(str(bin(number))[2:][::-1], base=2)))


if __name__ == '__main__':
    import sys

    print(solve(max_digits=int(sys.argv[1])))
