#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 33: Digit Cancelling Fractions.

  Problem Statement:
    The fraction 49/98 is a curious fraction, as an inexperienced mathematician in
    attempting to simplify it may incorrectly believe that 49/98 = 4/8, which is
    correct, is obtained by cancelling the 9 s.

    We shall consider fractions like, 30/50 = 3/5, to be trivial examples.

    There are exactly four non-trivial examples of this type of fraction, less
    than one in value, and containing two digits in the numerator and
    denominator.

    If the product of these four fractions is given in its lowest common terms,
    find the value of the denominator.

  Solution Approach:
    To solve this problem, first understand the concept of digit cancelling
    fractions where incorrectly cancelling digits yields a correct simplified
    fraction. Focus on fractions with two digits in numerator and denominator,
    less than one in value. Avoid trivial cases like fractions ending with zero.

    The approach involves iterating through all two-digit numerators and
    denominators, checking for non-trivial digit cancelling cases that maintain
    equivalence. Multiply these fractions and reduce the product to lowest terms
    by computing the greatest common divisor (GCD). Return the denominator of
    the simplified product. Efficient checking and careful handling of digit
    cancellation scenarios are key.

  Test Cases:
    main:
      answer=100.


  Answer: 100
  URL: https://projecteuler.net/problem=33
"""
from __future__ import annotations

from fractions import Fraction
from functools import reduce

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=33, test_case_category=TestCaseCategory.EXTENDED)
def digit_cancelling_fractions() -> int:
    return reduce(lambda a, b: a * b, (Fraction(numerator, denominator) for denominator in range(2, 10) for numerator in
                                       range(1, denominator) for x in range(1, 10) if denominator != x != numerator if
                                       (10 * numerator + x) * denominator == (10 * x + denominator) * numerator),
                  Fraction(1, 1)).denominator


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=33, time_out_in_seconds=300, mode='evaluate'))
