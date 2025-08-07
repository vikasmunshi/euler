#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 38: Pandigital Multiples.

  Problem Statement:
    Take the number 192 and multiply it by each of 1, 2, and 3:

        192 x 1 = 192
        192 x 2 = 384
        192 x 3 = 576

    By concatenating each product we get the 1 to 9 pandigital, 192384576.
    We will call 192384576 the concatenated product of 192 and (1, 2, 3).

    The same can be achieved by starting with 9 and multiplying by 1, 2, 3, 4,
    and 5, giving the pandigital, 918273645, which is the concatenated product
    of 9 and (1, 2, 3, 4, 5).

    What is the largest 1 to 9 pandigital 9-digit number that can be formed as
    the concatenated product of an integer with (1, 2, ..., n) where n > 1?

  Solution Approach:
    To solve this problem, consider generating concatenated products for a range
    of integers multiplied by sequences of increasing length starting from 2. For
    each integer, concatenate the products of it multiplied by 1, 2, ..., n until
    the concatenated string reaches nine digits. Check if this resulting 9-digit
    number is pandigital, containing each digit from 1 to 9 exactly once. Keep
    track of the largest such pandigital number found. Efficiently prune the search
    by considering the numeric range that can produce a 9-digit concatenated product
    and leverage string manipulation and set operations to verify pandigitality.

  Test Cases:
    main:
      answer=932718654.


  Answer: 932718654
  URL: https://projecteuler.net/problem=38
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.pandigital_numbers import is_nine_pandigital
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=38, test_case_category=TestCaseCategory.EXTENDED)
def pandigital_multiples() -> int:
    for n, x in ((2, 9876), (3, 987), (4, 98), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)):
        while x > 0:
            number = ''.join([str(i * x) for i in range(1, n + 1)])
            if is_nine_pandigital(number):
                return int(number)
            x -= 1
    raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=38, time_out_in_seconds=300, mode='evaluate'))
