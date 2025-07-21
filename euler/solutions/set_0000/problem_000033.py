#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 33: Digit cancelling fractions

Problem Statement:
The fraction 49/98 is a curious fraction, as an inexperienced mathematician in attempting
to simplify it may incorrectly believe that 49/98 = 4/8, which is correct, is obtained by
cancelling the 9s.

We shall consider fractions like, 30/50 = 3/5, to be trivial examples.

There are exactly four non-trivial examples of this type of fraction, less than one in value,
and containing two digits in the numerator and denominator.

If the product of these four fractions is given in its lowest common terms, find the value
of the denominator.

Solution Approach:
This solution systematically tests all possible two-digit fractions to find those that satisfy
the curious property of digit cancellation:

1. Generate all possible combinations of single-digit numerators and denominators where the
   numerator is less than the denominator (to ensure the fraction is less than 1).

2. For each valid digit pair, try all possible shared digits to form two-digit numbers in
   both numerator and denominator.

3. Test if incorrectly canceling the shared digit results in a value equal to the original fraction.
   For digits a, b, and x, we check if (10a + x)/(10x + b) = a/b.

4. Filter out trivial examples (where the shared digit is 0).

5. Calculate the product of all valid curious fractions using Python's Fraction class to maintain
   exact values and automatic simplification.

6. Return the denominator of the resulting product in its lowest form.

The implementation uses functional programming concepts with Python's reduce function to efficiently
combine the fractions and find the final result.

URL: https://projecteuler.net/problem=33
Answer: 100
"""
from fractions import Fraction
from functools import reduce

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=33)
problem_number: int = 33

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=100, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def denominator_product_curious_fractions() -> int:
    """Find the denominator of the product of four curious fractions in the lowest common terms.

    This function identifies the four non-trivial digit-cancelling fractions and returns the
    denominator of their product when expressed in lowest terms.

    Returns:
        The denominator of the product of the four curious fractions in lowest form

    Example:
        >>> denominator_product_curious_fractions()
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
    raise SystemExit(evaluate_solutions(problem_number))
