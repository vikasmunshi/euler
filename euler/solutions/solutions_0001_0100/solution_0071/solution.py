#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 71: Ordered Fractions.

  Problem Statement:
    Consider the fraction, n over d, where n and d are positive integers. If n
    is less than d and the highest common factor of n and d is 1, it is called
    a reduced proper fraction.

    If we list the set of reduced proper fractions for d less than or equal to 8
    in ascending order of size, we get:
    1 over 8, 1 over 7, 1 over 6, 1 over 5, 1 over 4, 2 over 7, 1 over 3, 3 over 8,
    2 over 5, 3 over 7, 1 over 2, 4 over 7, 3 over 5, 5 over 8, 2 over 3, 5 over
    7, 3 over 4, 4 over 5, 5 over 6, 6 over 7, 7 over 8.

    It can be seen that 2 over 5 is the fraction immediately to the left of 3 over
    7.

    By listing the set of reduced proper fractions for d less than or equal to
    1,000,000 in ascending order of size, find the numerator of the fraction
    immediately to the left of 3 over 7.

  Solution Approach:
    This problem involves finding the reduced proper fraction immediately
    to the left of a given target fraction (3/7) within the set of fractions
    with denominators up to a large limit (1,000,000).

    A practical approach is to use the concept of farey sequences or mediant
    properties to search efficiently without enumerating all fractions.
    Since fractions are reduced, greatest common divisor (GCD) checks help
    ensure validity.

    One way is to iterate over denominators up to the limit and calculate the
    best possible numerator n such that n/d is less than 3/7, then track the
    fraction closest to 3/7 from the left side.

    Efficient computations of GCD and careful fraction comparison will help
    maintain performance. This approach avoids generating and sorting the
    entire list of fractions.

    The problem tests number theory understanding, especially knowledge of
    coprime integers, fraction ordering, and optimization techniques to handle
    large search spaces.

  Test Cases:
    preliminary:
      max_d=10,
      answer=2.

    main:
      max_d=1000000,
      answer=428570.

    extended:
      max_d=1000000000,
      answer=428571425.

      max_d=1000000000000,
      answer=428571428570.


  Answer: 428570
  URL: https://projecteuler.net/problem=71
"""
from __future__ import annotations

from fractions import Fraction

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


@register_solution(euler_problem=71, test_case_category=TestCaseCategory.EXTENDED)
def ordered_fractions(*, max_d: int) -> int:
    result: Fraction = Fraction(3, 7) - Fraction(1, 7 * (max_d // 7))
    if show_solution():
        difference = Fraction(3, 7) - result
        print(f'Solution for max_d={max_d!r}: result={result!r} difference={difference!r} '
              f'result.numerator={result.numerator!r}')
    return result.numerator


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=71, time_out_in_seconds=300, mode='evaluate'))
