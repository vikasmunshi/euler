#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 36: Double Base Palindromes.

  Problem Statement:
    The decimal number, 585 = 1001001001_2 (binary), is palindromic in
    both bases.

    Find the sum of all numbers, less than one million, which are
    palindromic in base 10 and base 2.

    (Please note that the palindromic number, in either base, may not
    include leading zeros.)

  Solution Approach:
    To solve this problem, first understand what it means for a number
    to be palindromic in two different bases (decimal and binary). You
    will need to generate or test numbers less than one million to check
    if they satisfy this property.

    To efficiently check for palindromes, create helper functions that
    can convert a number to a string in the desired base and verify if
    that string reads the same forwards and backwards.

    Consider iterating through all numbers under one million, checking
    both their decimal and binary representations for the palindrome
    property.

    Accumulate these numbers to find the sum.

    Be mindful that palindromic numbers must not have leading zeros in
    either base representation.

    This approach combines number theory concepts (palindromes) and
    efficient string manipulation or mathematical checks for palindrome
    validation.

  Test Cases:
    preliminary:
      max_digits=1,
      answer=25.

      max_digits=2,
      answer=157.

      max_digits=3,
      answer=1772.

      max_digits=4,
      answer=18228.

    main:
      max_digits=6,
      answer=872187.

    extended:
      max_digits=9,
      answer=2609044274.


  Answer: 872187
  URL: https://projecteuler.net/problem=36
"""
from __future__ import annotations

from typing import Generator

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


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


@register_solution(euler_problem=36, test_case_category=TestCaseCategory.EXTENDED)
def double_base_palindromes(*, max_digits: int) -> int:
    return sum((number for number in generate_decimal_palindromes(max_digits) if
                number == int(str(bin(number))[2:][::-1], base=2)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=36, time_out_in_seconds=300, mode='evaluate'))
