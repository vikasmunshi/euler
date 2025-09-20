#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
URL: https://projecteuler.net/problem=36
"""
from __future__ import annotations

from typing import Any, Generator

from euler_solver.framework import evaluate, logger, register_solution

euler_problem: int = 36
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'max_digits': 1}, 'answer': 25},
    {'category': 'dev', 'input': {'max_digits': 2}, 'answer': 157},
    {'category': 'dev', 'input': {'max_digits': 3}, 'answer': 1772},
    {'category': 'dev', 'input': {'max_digits': 4}, 'answer': 18228},
    {'category': 'main', 'input': {'max_digits': 6}, 'answer': 872187},
    {'category': 'extra', 'input': {'max_digits': 9}, 'answer': 2609044274},
]


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


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_double_base_palindromes_p0036_s0(*, max_digits: int) -> int:
    return sum((number for number in generate_decimal_palindromes(max_digits) if
                number == int(str(bin(number))[2:][::-1], base=2)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
