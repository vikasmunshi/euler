#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 80: Square Root Digital Expansion.

  Problem Statement:
    It is well known that if the square root of a natural number is not an
    integer, then it is irrational. The decimal expansion of such square
    roots is infinite without any repeating pattern at all.

    The square root of two is 1.41421356237309504880..., and the digital sum
    of the first one hundred decimal digits is 475.

    For the first one hundred natural numbers, find the total of the digital
    sums of the first one hundred decimal digits for all the irrational
    square roots.

  Solution Approach:
    To solve this problem, first understand that only natural numbers
    which are perfect squares have rational square roots with finite
    decimal expansions. For all other natural numbers, the square roots
    are irrational with infinite non-repeating decimal expansions.

    The key is to compute the decimal expansion of the square root for
    each natural number up to 100, excluding perfect squares. Since the
    decimal expansion is infinite, use an algorithm or numerical method
    that allows you to extract each decimal digit accurately up to 100
    digits.

    Methods like the digit-by-digit calculation of square roots, or
    utilizing high-precision arithmetic with Python's decimal module,
    can be effective.

    After computing the digits, sum the first 100 decimal digits for each
    irrational root, then accumulate these sums for the total.

    Efficiently identifying perfect squares and managing precision are
    important to ensure correctness and performance.

  Test Cases:
    preliminary:
      digits=100,
      max_num=2,
      answer=475.

    main:
      digits=100,
      max_num=99,
      answer=40886.

    extended:
      digits=100,
      max_num=999,
      answer=434576.


  Answer: 40886
  URL: https://projecteuler.net/problem=80
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.sqrt import sqrt_binary_search, sqrt_heron_method
from euler.maths.sum_digits import sum_digits
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=80, test_case_category=TestCaseCategory.EXTENDED)
def square_root_digital_expansion_sqrt_heron_method(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i ** 0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
    return result


@register_solution(euler_problem=80, test_case_category=TestCaseCategory.EXTENDED)
def square_root_digital_expansion_sqrt_binary_search(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i ** 0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_binary_search(i, digits))
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=80, time_out_in_seconds=300, mode='evaluate'))
