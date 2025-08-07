#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 16: Power Digit Sum.

  Problem Statement:
    2^15 = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.

    What is the sum of the digits of the number 2^1000?

  Solution Approach:
    To solve this problem, you need to compute the number 2 raised to the power of 1000.
    Since this number is very large, it cannot be handled by standard integer types in
    many programming languages, so you should use arbitrary-precision arithmetic or
    built-in large integer support. After computing the power, convert the resulting
    number to a string to access each digit individually. Sum these digits to find the
    answer. Efficient methods for exponentiation, such as exponentiation by squaring,
    can be used to optimize the calculation if needed.

  Test Cases:
    preliminary:
      base=2,
      power=15,
      answer=26.

    main:
      base=2,
      power=1000,
      answer=1366.

    extended:
      base=2,
      power=10000,
      answer=13561.


  Answer: 1366
  URL: https://projecteuler.net/problem=16
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=16, test_case_category=TestCaseCategory.EXTENDED)
def power_digit_sum(*, base: int, power: int) -> int:
    return sum((int(i) for i in str(base ** power)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=16, time_out_in_seconds=300, mode='evaluate'))
