#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 52: Permuted Multiples.

  Problem Statement:
    It can be seen that the number, 125874, and its double, 251748, contain
    exactly the same digits, but in a different order.

    Find the smallest positive integer, x, such that 2 x x, 3 x x, 4 x x,
    5 x x, and 6 x x, contain the same digits.

  Solution Approach:
    To solve this problem, consider iterating through positive integers
    and for each integer, generate its multiples from 2x up to 6x. Convert
    each multiple to a string and compare the sorted digits to ensure they
    are identical. The first integer for which all these multiples contain
    the same digits in a different order is the solution. Efficient
    digit comparison and early rejection of candidates can speed up the
    search process. This approach leverages string manipulation and
    sorting techniques and ensures that the solution is found without
    excessive computational effort.

  Test Cases:
    preliminary:
      multiples=2,
      answer=125874.

      multiples=3,
      answer=142857.

      multiples=4,
      answer=142857.

      multiples=5,
      answer=142857.

    main:
      multiples=6,
      answer=142857.


  Answer: 142857
  URL: https://projecteuler.net/problem=52
"""
from __future__ import annotations

import sys

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=52, test_case_category=TestCaseCategory.EXTENDED)
def permuted_multiples(*, multiples: int) -> int:
    if not (isinstance(multiples, int) and 1 < multiples < 7):
        raise ValueError('multiples must be an integer between 2 and 6, both inclusive.')
    multiples_range = tuple(range(1, multiples + 1))
    for i in range(1, sys.maxsize // multiples):
        if len({''.join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
            return i
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=52, time_out_in_seconds=300, mode='evaluate'))
