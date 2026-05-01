#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
URL: https://projecteuler.net/problem=80
"""
from __future__ import annotations

from typing import Any

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 80
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'digits': 100, 'max_num': 2}, 'answer': 475},
    {'category': 'main', 'input': {'digits': 100, 'max_num': 99}, 'answer': 40886},
    {'category': 'extra', 'input': {'digits': 100, 'max_num': 999}, 'answer': 434576},
]


def sum_digits(n: str) -> int:
    return sum(int(digit) for digit in n)


def sqrt_heron_method(number: int, digits: int) -> str:
    # Handle special case of zero
    if number == 0:
        return '0' * min(1, digits)

    # Validate input
    if number < 0:
        raise ValueError(f'Cannot calculate square root of negative number: {number}')

    number *= 10 ** (2 * digits)
    sqrt = number
    while sqrt != (sqrt := (sqrt + number // sqrt) // 2):
        pass
    return str(sqrt)[:digits]


def sqrt_binary_search(number: int, digits: int) -> str:
    # Handle special case of zero
    if number == 0:
        return '0' * min(1, digits)

    # Validate input
    if number < 0:
        raise ValueError(f'Cannot calculate square root of negative number: {number}')

    # Scale the number to get desired precision
    scaled_number = number * (10 ** (2 * digits))

    # Set binary search boundaries
    low = 0
    high = scaled_number

    # Binary search loop
    while high - low > 1:
        mid = (low + high) // 2
        if mid * mid <= scaled_number:
            low = mid
        else:
            high = mid

    # Return the result with the correct number of digits
    return str(low)[:digits]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_square_root_digital_expansion_p0080_s0(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i ** 0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
    return result


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_square_root_digital_expansion_p0080_s1(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i ** 0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_binary_search(i, digits))
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
