#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0080/p0080.py :: solve_square_root_digital_expansion_p0080_s0.

Project Euler Problem 80: Square Root Digital Expansion.

Problem Statement:
    It is well known that if the square root of a natural number is not an integer,
    then it is irrational. The decimal expansion of such square roots is infinite
    without any repeating pattern at all.

    The square root of two is 1.41421356237309504880..., and the digital sum of the
    first one hundred decimal digits is 475.

    For the first one hundred natural numbers, find the total of the digital sums of
    the first one hundred decimal digits for all the irrational square roots.

Solution Approach:
    Use high-precision arithmetic or digit-by-digit algorithms to compute the first 100
    decimal digits of square roots for non-square natural numbers. Sum the digits for
    each, then total over all. Efficient big integer arithmetic and digit extraction
    methods based on long division or Newton iteration are key.

Answer: 40886
URL: https://projecteuler.net/problem=80"""
from __future__ import annotations


def sum_digits(n: str) -> int:
    return sum((int(digit) for digit in n))


def sqrt_heron_method(number: int, digits: int) -> str:
    if number == 0:
        return '0' * min(1, digits)
    if number < 0:
        raise ValueError(f'Cannot calculate square root of negative number: {number}')
    number *= 10 ** (2 * digits)
    sqrt = number
    while sqrt != (sqrt := ((sqrt + number // sqrt) // 2)):
        pass
    return str(sqrt)[:digits]


def solve(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i ** 0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
    return result


if __name__ == '__main__':
    import sys

    print(solve(digits=int(sys.argv[1]), max_num=int(sys.argv[2])))
