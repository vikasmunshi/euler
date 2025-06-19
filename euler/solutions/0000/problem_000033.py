#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 33
# https://projecteuler.net/problem=33
# Answer: 100
# Notes: 
import textwrap
from fractions import Fraction
from functools import reduce
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},
        answer=100,
    ),
]


def solution() -> int:
    """Find the denominator of the product of four curious fractions in the lowest common terms.

    A curious fraction is one where incorrectly canceling a common digit in both the numerator 
    and denominator (like canceling the 9s in 49/98) actually gives the correct result (4/8).
    We're looking for fractions that are:
    1. Less than 1 (numerator < denominator)
    2. Have two digits in both numerator and denominator
    3. Non-trivial (not like 30/50 where canceling gives 3/5 by normal simplification)

    Algorithm:
    1. Generate all possible single-digit numerators and denominators (excluding trivial cases)
    2. For each pair, try all possible shared digits to form two-digit numbers
    3. Test if incorrectly canceling the shared digit gives the same value as the original fraction
    4. Multiply all valid curious fractions together using the Fraction class to maintain exact values
    5. Return the denominator of the resulting fraction in its lowest terms

    Mathematical formulation:
    - For a digit x and single digits a and b, we test if (10a + x)/(10x + b) = a/b
    - This can be rearranged as: (10a + x)*b = (10x + b)*a
    - Which simplifies to: 10ab + xb = 10xa + ba

    Returns:
        The denominator of the product of the four curious fractions in the lowest common terms
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


solution = cast(SolutionProtocol, solution)

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 33
https://projecteuler.net/problem=33
The fraction 49/98 is a curious fraction, 
as an inexperienced mathematician in attempting to simplify it may incorrectly believe that 49/98 = 4/8, 
which is correct, is obtained by cancelling the 9s.
We shall consider fractions like, 30/50 = 3/5, to be trivial examples.
There are exactly four non-trivial examples of this type of fraction, less than one in value,
and containing two digits in the numerator and denominator.
If the product of these four fractions is given in its lowest common terms, find the value of the denominator.

    Algorithm:
    1. Generate all possible single-digit numerators and denominators (excluding trivial cases)
    2. For each pair, try all possible shared digits to form two-digit numbers
    3. Test if incorrectly canceling the shared digit gives the same value as the original fraction
    4. Multiply all valid curious fractions together using the Fraction class to maintain exact values
    5. Return the denominator of the resulting fraction in its lowest terms

''').strip()

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
