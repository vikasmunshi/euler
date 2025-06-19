#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 32
# https://projecteuler.net/problem=32
# Answer: 45228
# Notes: 
import textwrap
from itertools import permutations
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},
        answer=45228,
    ),
]

digits = ('1', '2', '3', '4', '5', '6', '7', '8', '9')


def sum_pandigital_products() -> int:
    """Calculate the sum of all products whose multiplicand/multiplier/product identity is 1-9 pandigital.

    A pandigital product identity is an equation a × b = c where the digits used in a, b, and c 
    together use each digit from 1-9 exactly once. For example, 39 × 186 = 7254 is pandigital
    because the digits 1-9 are used exactly once across all three numbers.

    Algorithm:
    1. Consider only the possible valid configurations for digit lengths:
       - 1-digit × 4-digit = 4-digit product
       - 2-digit × 3-digit = 4-digit product
       (Other combinations would have too many or too few digits to be valid)
    2. Generate permutations of digits for multiplicands and multipliers of appropriate lengths
    3. Calculate the product for each valid pair
    4. Check if the combined digits of multiplicand, multiplier, and product form a 1-9 pandigital
    5. Use a set to ensure each product is counted only once (as required by the problem)
    6. Sum the unique products that satisfy the pandigital condition

    Returns:
        The sum of all unique products that can be written as part of a 1-9 pandigital identity
    """
    return sum(set(
        c
        for a_len, b_len in ((1, 4), (2, 3))
        for a in permutations(digits, a_len)
        for b in permutations((d for d in digits if d not in a), b_len)
        if ''.join(sorted((a_str := ''.join(a)) + (b_str := ''.join(b)) + str(c := (int(a_str) * int(b_str)))))
        == '123456789'))


solution = cast(SolutionProtocol, sum_pandigital_products)

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 32
https://projecteuler.net/problem=32
We shall say that an n-digit number is pandigital if it makes use of all the digits 1 to n exactly once;
for example, the 5-digit number, 15234, is 1 through 5 pandigital.

The product 7254 is unusual, as the identity, 39 * 186 = 7254, containing multiplicand, multiplier,
and product is 1 through 9 pandigital.

Find the sum of all products whose multiplicand/multiplier/product identity can be written as a 1 through 9 pandigital.

HINT: Some products can be obtained in more than one way so be sure to only include it once in your sum.

    Algorithm:
    1. Consider only the possible valid configurations for digit lengths:
       - 1-digit × 4-digit = 4-digit product
       - 2-digit × 3-digit = 4-digit product
       (Other combinations would have too many or too few digits to be valid)
    2. Generate permutations of digits for multiplicands and multipliers of appropriate lengths
    3. Calculate the product for each valid pair
    4. Check if the combined digits of multiplicand, multiplier, and product form a 1-9 pandigital
    5. Use a set to ensure each product is counted only once (as required by the problem)
    6. Sum the unique products that satisfy the pandigital condition

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
