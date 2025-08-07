#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 4: Largest Palindrome Product.

  Problem Statement:
    A palindromic number reads the same both ways. The largest palindrome made from
    the product of two 2-digit numbers is 9009 = 91 x 99.

    Find the largest palindrome made from the product of two 3-digit numbers.

  Solution Approach:
    To solve this problem, consider iterating over all products of two 3-digit
    numbers, starting from 999 down to 100. For each product, check if it is a
    palindrome by converting the number to a string and verifying if it reads the
    same forwards and backwards. Keep track of the largest palindrome found. You
    can optimize by starting with larger numbers and breaking early if the product
    is smaller than the current largest palindrome, reducing unnecessary checks.
    This approach combines brute force with palindrome verification and mindful
    iteration to efficiently find the solution.
    Tip: Divisibility by 11.

  Test Cases:
    preliminary:
      n=2,
      answer=9009.

    main:
      n=3,
      answer=906609.

    extended:
      n=4,
      answer=99000099.

      n=5,
      answer=9966006699.


  Answer: 906609
  URL: https://projecteuler.net/problem=4
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


def is_palindromic(*, number: int) -> bool:
    str_number: str = str(number)
    return str_number == ''.join(reversed(str_number))


@register_solution(euler_problem=4, test_case_category=TestCaseCategory.EXTENDED)
def largest_palindrome_product(*, n: int) -> int:
    largest_palindrome: int = 0
    a_max: int = 0
    b_max: int = 0
    max_number: int = 10 ** n - 1
    min_number: int = 10 ** (n - 1)
    max_multiple_11 = max_number - max_number % 11
    for a in range(max_number, min_number, -1):
        a_is_multiple_11 = a % 11 == 0
        for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
            ab = a * b
            if ab <= largest_palindrome:
                break
            if is_palindromic(number=ab):
                a_max, b_max, largest_palindrome = (a, b, ab)
    if show_solution():
        print(f'Largest palindrome that is a multiple of two {n}-digit numbers is '
              f'{largest_palindrome} ({a_max}x{b_max})')
    return largest_palindrome


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=4, time_out_in_seconds=300, mode='evaluate'))
