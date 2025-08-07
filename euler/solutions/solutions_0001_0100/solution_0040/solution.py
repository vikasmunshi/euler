#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 40: Champernownes Constant.

  Problem Statement:
    An irrational decimal fraction is created by concatenating the positive integers:
    0.12345678910 1112131415161718192021 ...

    It can be seen that the 12th digit of the fractional part is 1.

    If d_n represents the nth digit of the fractional part, find the value
    of the following expression.
    d_1 x d_10 x d_100 x d_1000 x d_10000 x d_100000 x d_1000000

  Solution Approach:
    To solve this problem, first understand how the concatenated decimal
    (Champernowne's constant) is constructed by joining positive integers.
    The key task is to find the digit at specific positions efficiently.

    Calculate the ranges of digit lengths (1-digit, 2-digit numbers, etc.)
    and determine which range contains the desired digit position.
    Then, identify the exact integer and its digit that corresponds to that
    position. Finally, multiply the retrieved digits as required.

    This approach requires careful index calculations and handling of
    number lengths but avoids constructing the entire string, making
    it efficient for large digit positions.

  Test Cases:
    preliminary:
      i=1,
      answer=1.

      i=2,
      answer=5.

      i=3,
      answer=15.

      i=4,
      answer=105.

      i=5,
      answer=210.

      i=6,
      answer=210.

    main:
      i=7,
      answer=1470.

    extended:
      i=8,
      answer=11760.

      i=9,
      answer=11760.

      i=10,
      answer=11760.

      i=11,
      answer=0.


  Answer: 1470
  URL: https://projecteuler.net/problem=40
"""
from __future__ import annotations

from functools import reduce

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


def get_nth_digit_champernowne_s_constant(n: int) -> int:
    length_till_num_digits, length_with_num_digits, num_digits = (0, 0, 0)
    while length_with_num_digits < n:
        num_digits += 1
        length_till_num_digits = length_with_num_digits
        length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)
    offset_of_number = n - length_till_num_digits - 1
    digit_in_number = offset_of_number % num_digits
    number = 10 ** (num_digits - 1) + offset_of_number // num_digits
    return int(str(number)[digit_in_number])


@register_solution(euler_problem=40, test_case_category=TestCaseCategory.EXTENDED)
def champernowne_s_constant(*, i: int) -> int:
    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10 ** i) for i in range(0, i + 1)), 1)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=40, time_out_in_seconds=300, mode='evaluate'))
