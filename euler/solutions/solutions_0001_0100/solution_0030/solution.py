#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 30: Digit Fifth Powers.

  Problem Statement:
    Surprisingly there are only three numbers that can be written as the sum of
    fourth powers of their digits:

        1634 = 1^4 + 6^4 + 3^4 + 4^4
        8208 = 8^4 + 2^4 + 0^4 + 8^4
        9474 = 9^4 + 4^4 + 7^4 + 4^4

    As 1 = 1^4 is not a sum it is not included.

    The sum of these numbers is 1634 + 8208 + 9474 = 19316.

    Find the sum of all the numbers that can be written as the sum of fifth
    powers of their digits.

  Solution Approach:
    To solve this problem, consider each number and check whether it
    can be expressed as the sum of the fifth powers of its digits. The approach
    involves iterating through numbers starting from 2 (since 1 is not included),
    and for each number, split it into its individual digits, compute the fifth
    power of each digit, and check if the sum of these powers equals the original
    number.

    Since the value grows rapidly, establish an upper bound beyond which no
    number can equal the sum of the fifth powers of its digits. This upper bound
    can be estimated based on the maximum digit power multiplied by the number
    of digits.

    Use efficient looping and digit extraction techniques to avoid excessive
    computation. Summation of the qualifying numbers at the end will yield the
    final result.

  Test Cases:
    preliminary:
      n=4,
      answer=19316.

    main:
      n=5,
      answer=443839.


  Answer: 443839
  URL: https://projecteuler.net/problem=30
"""
from __future__ import annotations

from itertools import combinations_with_replacement
from math import ceil, log

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=30, test_case_category=TestCaseCategory.EXTENDED)
def digit_fifth_powers(*, n: int) -> int:
    upper_bound_num_digits = ceil(log(n * 9 ** n, 10))
    return sum((num for digits in combinations_with_replacement(range(10), upper_bound_num_digits) if
                (num := sum((x ** n for x in digits))) > 9 and num == sum((int(x) ** n for x in str(num)))))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=30, time_out_in_seconds=300, mode='evaluate'))
