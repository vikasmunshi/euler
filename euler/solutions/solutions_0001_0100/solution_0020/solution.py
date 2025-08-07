#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 20: Factorial Digit Sum.

  Problem Statement:
    n! means n x (n - 1) x ... x 3 x 2 x 1.

    For example, 10! = 10 x 9 x ... x 3 x 2 x 1 = 3628800, and the sum of the
    digits in the number 10! is 3 + 6 + 2 + 8 + 8 + 0 + 0 = 27.

    Find the sum of the digits in the number 100!.

  Solution Approach:
    To solve the problem of finding the sum of the digits of 100!, first compute
    the factorial of 100. Since 100! is an extremely large number that cannot be
    handled by standard integer data types, use arbitrary-precision arithmetic
    available in many programming languages.

    After computing 100!, convert the resulting number to a string to iterate
    over each digit. Sum these digits to get the final answer.

    Efficient algorithms for factorial computation and string manipulation will
    be helpful, but the main focus is on handling big integers and digit summation.

  Test Cases:
    preliminary:
      n=10,
      answer=27.

    main:
      n=100,
      answer=648.


  Answer: 648
  URL: https://projecteuler.net/problem=20
"""
from __future__ import annotations

from math import factorial

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=20, test_case_category=TestCaseCategory.EXTENDED)
def factorial_digit_sum(*, n: int) -> int:
    return sum((int(d) for d in str(factorial(n))))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=20, time_out_in_seconds=300, mode='evaluate'))
