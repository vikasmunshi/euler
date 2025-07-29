#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 33: digit_cancelling_fractions

Problem Statement:
  The fraction 49/98 is a curious fraction, as an inexperienced mathematician in
  attempting to simplify it may incorrectly believe that 49/98 = 4/8, which is
  correct, is obtained by cancelling the 9s. We shall consider fractions like,
  30/50 = 3/5, to be trivial examples. There are exactly four non-trivial examples
  of this type of fraction, less than one in value, and containing two digits in
  the numerator and denominator. If the product of these four fractions is given
  in its lowest common terms, find the value of the denominator.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=33
Answer: None
"""
from __future__ import annotations

from fractions import Fraction
from functools import reduce

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=100,
        is_main_case=False,
        kwargs={},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #33
@register_solution(problem_number=33, test_cases=test_cases)
def digit_cancelling_fractions() -> int:
    """Find the denominator of the product of four curious fractions in the lowest common terms.

    This function identifies the four non-trivial digit-cancelling fractions and returns the
    denominator of their product when expressed in lowest terms.

    Returns:
        The denominator of the product of the four curious fractions in lowest form

    Example:
        >>> digit_cancelling_fractions()
        100
    """
    return reduce(lambda a, b: a * b,  # function
                  (  # sequence generator
                      Fraction(numerator, denominator)
                      for denominator in range(2, 10)
                      for numerator in range(1, denominator)
                      for x in range(1, 10) if denominator != x != numerator
                      if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator
                  ),
                  Fraction(1, 1)  # initial
                  ).denominator


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(33))
