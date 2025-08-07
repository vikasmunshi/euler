#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 32: Pandigital Products.

  Problem Statement:
    We shall say that an n-digit number is pandigital if it makes use of all the
    digits 1 to n exactly once; for example, the 5-digit number, 15234, is 1
    through 5 pandigital.

    The product 7254 is unusual, as the identity, 39 x 186 = 7254, containing
    multiplicand, multiplier, and product is 1 through 9 pandigital.

    Find the sum of all products whose multiplicand/multiplier/product identity
    can be written as a 1 through 9 pandigital.

    HINT: Some products can be obtained in more than one way so be sure to
    only include it once in your sum.

  Solution Approach:
    To solve this problem, consider the concept of pandigital numbers, which
    are numbers that contain each digit in a given range exactly once. The key
    challenge is to find all unique products whose multiplicand, multiplier, and
    product together form a 1 through 9 pandigital combination.

    An effective approach involves generating all possible combinations of
    multiplicand and multiplier pairs that use distinct digits 1 to 9 without
    repetition, then calculating their product. Check if the concatenation of
    the multiplicand, multiplier, and product contains all digits from 1 to 9
    exactly once.

    Tracking duplicates is crucial, as a product might be expressible in multiple
    ways. Store unique products in a set to avoid counting them multiple times.

    The problem is computational but can be optimized by reasoning about the
    lengths of multiplicand and multiplier and limiting search space accordingly.
    This involves combinatorial enumeration and careful digit usage checks.

    Overall, this task combines number theory, combinatorics, and efficient
    search algorithms to find the required sum.

  Test Cases:
    main:
      answer=45228.


  Answer: 45228
  URL: https://projecteuler.net/problem=32
"""
from __future__ import annotations

from itertools import permutations

from euler.logger import logger
from euler.maths.pandigital_numbers import is_nine_pandigital, nine_digits
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=32, test_case_category=TestCaseCategory.EXTENDED)
def pandigital_products() -> int:
    return sum(set((c
                    for a_len, b_len in ((1, 4), (2, 3))
                    for a in permutations(nine_digits, a_len)
                    for b in permutations((d for d in nine_digits if d not in a), b_len)
                    if is_nine_pandigital((a_str := ''.join(a)) + (b_str := ''.join(b))
                                          + str(c := int(a_str) * int(b_str))))))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=32, time_out_in_seconds=300, mode='evaluate'))
