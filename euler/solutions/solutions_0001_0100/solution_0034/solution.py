#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 34: Digit Factorials.

  Problem Statement:
    145 is a curious number, as 1! + 4! + 5! = 1 + 24 + 120 = 145.

    Find the sum of all numbers which are equal to the sum of the factorial of
    their digits.

    Note: As 1! = 1 and 2! = 2 are not sums they are not included.

  Solution Approach:
    To solve this problem, start by understanding the factorial function and how
    to compute factorials of digits efficiently, possibly caching the results.
    Next, generate candidate numbers and for each, calculate the sum of the
    factorials of its digits. Compare this sum to the original number to check
    equality. An upper bound can be established because beyond a certain number
    of digits, the sum of factorials of digits will be smaller than the number
    itself. This allows limiting the search space systematically. Summing all
    such numbers that meet the condition will yield the answer.

  Test Cases:
    main:
      answer=40730.


  Answer: 40730
  URL: https://projecteuler.net/problem=34
"""
from __future__ import annotations

from itertools import combinations_with_replacement

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=34, test_case_category=TestCaseCategory.EXTENDED)
def digit_factorials() -> int:
    upper_bound_num_digits = 7 + 1
    factorial = {'0': 1, '1': 1, '2': 2, '3': 6, '4': 24, '5': 120, '6': 720, '7': 5040, '8': 40320, '9': 362880}
    return sum((int(num) for num_digits in range(2, upper_bound_num_digits) for digits in
                combinations_with_replacement('0123456789', num_digits) for num in
                (str(sum((factorial[d] for d in digits))),) if
                len(num) == num_digits and all((digit in num for digit in digits)) and (
                        num == str(sum((factorial[n] for n in num))))))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=34, time_out_in_seconds=300, mode='evaluate'))
