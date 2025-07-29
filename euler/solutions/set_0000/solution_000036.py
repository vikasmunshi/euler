#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 36: double_base_palindromes

Problem Statement:
  The decimal number, 585 = 1001001001_2 (binary), is palindromic in both bases.
  Find the sum of all numbers, less than one million, which are palindromic in
  base 10 and base 2. (Please note that the palindromic number, in either base,
  may not include leading zeros.)

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=36
Answer: None
"""
from __future__ import annotations

from typing import Generator

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase


def generate_decimal_palindromes(max_digits: int) -> Generator[int, None, None]:
    """Generate all decimal palindromes with up to max_digits digits.

    This function efficiently generates all palindromic numbers in base 10 with at most
    the specified number of digits. A palindrome reads the same forwards and backwards.

    The generation follows these steps:
    1. Yield all single-digit numbers (1-9) which are palindromes by definition
    2. Generate even-length palindromes by mirroring digits (e.g., 12 → 1221)
    3. Generate odd-length palindromes by inserting a middle digit (e.g., 12 → 12,321)

    Args:
        max_digits: The maximum number of decimal digits allowed in the palindromes

    Yields:
        All decimal palindromes with at most max_digits digits, in ascending order

    Examples:
        For max_digits=2, yields: 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33, ..., 99
        For max_digits=3, also includes: 101, 111, 121, ..., 999

    Notes:
        - Zero is not included as it would have a leading zero in binary
        - The algorithm avoids generating duplicates
        - The count of palindromes grows approximately as O(10^(max_digits/2))
    """
    # Generate single-digit palindromes (1-9)
    for digit in range(1, 10):
        yield digit

    # Generate multi-digit palindromes
    for digits in range(1, 10 ** (max_digits // 2)):
        digits_str = str(digits)
        digits_rev = digits_str[::-1]
        num_digits = len(digits_str)

        # Even-length palindromes (e.g., 1221, 123321)
        yield int(digits_str + digits_rev)

        # Odd-length palindromes (e.g., 12321, 1234321)
        # Only generate if we haven't exceeded max_digits
        if 2 * num_digits < max_digits:
            for mid_digit in '0123456789':
                yield int(digits_str + mid_digit + digits_rev)


test_cases: list[TestCase] = [
    TestCase(
        answer=25,
        is_main_case=False,
        kwargs={'max_digits': 1},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=157,
        is_main_case=False,
        kwargs={'max_digits': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1772,
        is_main_case=False,
        kwargs={'max_digits': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=18228,
        is_main_case=False,
        kwargs={'max_digits': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=872187,
        is_main_case=False,
        kwargs={'max_digits': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=2609044274,
        is_main_case=False,
        kwargs={'max_digits': 9},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #36
@register_solution(problem_number=36, test_cases=test_cases)
def double_base_palindromes(*, max_digits: int) -> int:
    """
    Find the sum of numbers that are palindromic in both decimal and binary bases.

    This solution efficiently generates decimal palindromes and checks if they are also
    palindromic in binary. A number is palindromic if it reads the same forwards and
    backwards. The approach avoids checking all numbers by directly generating palindromes.

    Args:
        max_digits: The maximum number of decimal digits to consider

    Returns:
        The sum of all double-base palindromes with at most max_digits decimal digits

    Example:
        >>> double_base_palindromes(max_digits=1)
        25
        >>> double_base_palindromes(max_digits=6)  # Original problem (< 1,000,000)
        872187
    """
    return sum(number for number in generate_decimal_palindromes(max_digits)
               if number == int(str(bin(number))[2:][::-1], base=2))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(36))
