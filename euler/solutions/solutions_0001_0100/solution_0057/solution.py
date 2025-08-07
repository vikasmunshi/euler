#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 57: Square Root Convergents.

  Problem Statement:
    It is possible to show that the square root of two can be expressed as an
    infinite continued fraction.

    sqrt 2 = 1 + 1 / (2 + 1 / (2 + 1 / (2 + ... )))

    By expanding this for the first four iterations, we get:

    1 + 1 / 2 = 3/2 = 1.5
    1 + 1 / (2 + 1 / 2) = 7/5 = 1.4
    1 + 1 / (2 + 1 / (2 + 1 / 2)) = 17/12 = 1.41666 ...
    1 + 1 / (2 + 1 / (2 + 1 / (2 + 1 / 2))) = 41/29 = 1.41379 ...

    The next three expansions are 99/70, 239/169, and 577/408, but the eighth
    expansion, 1393/985, is the first example where the number of digits in the
    numerator exceeds the number of digits in the denominator.

    In the first one-thousand expansions, how many fractions contain a numerator
    with more digits than the denominator?

  Solution Approach:
    To solve this problem, consider generating the sequence of convergents for the
    continued fraction representation of sqrt(2). Each convergent is a fraction
    expressed as numerator/denominator. Use a recurrence relation or iterative method
    that updates the numerator and denominator starting from initial terms.

    For each convergent, count the digits in the numerator and denominator. Compare
    the lengths to determine when the numerator contains more digits than the
    denominator.

    Efficient integer arithmetic is critical, as the numbers grow rapidly. You
    should avoid floating point approximations to maintain precision.

    Implement a loop to compute the first one-thousand expansions, tracking and
    counting the cases where the numerator has more digits than the denominator.

    This approach involves understanding continued fractions, working with large
    integer arithmetic, and performing digit length comparisons to achieve the
    required result.

  Test Cases:
    preliminary:
      expansions=10,
      answer=1.

      expansions=100,
      answer=15.

    main:
      expansions=1000,
      answer=153.

    extended:
      expansions=10000,
      answer=1508.


  Answer: 153
  URL: https://projecteuler.net/problem=57
"""
from __future__ import annotations

from sys import set_int_max_str_digits

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=57, test_case_category=TestCaseCategory.EXTENDED)
def square_root_convergents(*, expansions: int) -> int:
    numerator, denominator, result = (1, 1, 0)
    for _ in range(expansions):
        numerator, denominator = (numerator + 2 * denominator, numerator + denominator)
        try:
            result += len(str(numerator)) > len(str(denominator))
        except ValueError:
            set_int_max_str_digits(0)
            print(f'sys.set_int_max_str_digits(0) expansions={expansions!r}, '
                  f'len(str(numerator))={len(str(numerator))!r}, len(str(denominator))={len(str(denominator))!r}')
            result += len(str(numerator)) > len(str(denominator))
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=57, time_out_in_seconds=300, mode='evaluate'))
