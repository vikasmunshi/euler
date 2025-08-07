#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 24: Lexicographic Permutations.

  Problem Statement:
    A permutation is an ordered arrangement of objects. For example, 3124 is one
    possible permutation of the digits 1, 2, 3 and 4. If all of the permutations
    are listed numerically or alphabetically, we call it lexicographic order.
    The lexicographic permutations of 0, 1 and 2 are:

    012    021    102    120    201    210

    What is the millionth lexicographic permutation of the digits 0, 1, 2, 3, 4,
    5, 6, 7, 8 and 9?

  Solution Approach:
    To solve the problem of finding the millionth lexicographic permutation of the
    digits 0 through 9, one can use combinatorial mathematics rather than
    brute-force enumeration. The approach involves using factorial values to
    count how many permutations start with each digit, thereby determining the
    leading digit of the desired permutation. After fixing the first digit, the
    problem reduces to finding the lexicographic permutation within the
    remaining digits. This process repeats recursively or iteratively until the
    complete sequence is constructed. Efficient use of factorial computations and
    index manipulation allows direct calculation of the target permutation without
    generating all permutations explicitly.

  Test Cases:
    preliminary:
      digits=012,
      permutation_number=4,
      answer=120.

      digits=012,
      permutation_number=6,
      answer=210.

    main:
      digits=0123456789,
      permutation_number=1000000,
      answer=2783915460.


  Answer: 2783915460
  URL: https://projecteuler.net/problem=24
"""
from __future__ import annotations

from math import factorial

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=24, test_case_category=TestCaseCategory.EXTENDED)
def lexicographic_permutations(*, digits: str, permutation_number: int) -> str:
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, factorial(len(digits) - 1))
    result: str = digits[current] + lexicographic_permutations(digits=digits[:current] + digits[current + 1:],
                                                               permutation_number=remaining + 1)
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=24, time_out_in_seconds=300, mode='evaluate'))
