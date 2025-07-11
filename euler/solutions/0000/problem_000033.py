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

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=100, ),
]


def solution() -> int:
    """Find the denominator of the product of four curious fractions in the lowest common terms.

    This function identifies the four non-trivial digit-cancelling fractions and returns the
    denominator of their product when expressed in lowest terms.

    Returns:
        The denominator of the product of the four curious fractions in lowest form

    Example:
        >>> solution()
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
                  1  # initial
                  ).denominator


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
