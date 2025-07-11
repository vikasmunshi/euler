#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 32: Pandigital products

Problem Statement:
We shall say that an n-digit number is pandigital if it makes use of all the digits 1 to n
exactly once; for example, the 5-digit number, 15234, is 1 through 5 pandigital.

The product 7254 is unusual, as the identity, 39 × 186 = 7254, containing multiplicand,
multiplier, and product is 1 through 9 pandigital.

Find the sum of all products whose multiplicand/multiplier/product identity can be written
as a 1 through 9 pandigital.

HINT: Some products can be obtained in more than one way so be sure to only include it once in your sum.

Solution Approach:
This solution systematically explores the possible configurations for a 1-9 pandigital product:

1. Through mathematical reasoning, we can determine that only two configurations can possibly work:
   - 1-digit × 4-digit = 4-digit product
   - 2-digit × 3-digit = 4-digit product
   (Other configurations would use too many or too few digits to be valid)

2. The implementation uses the permutations function from the itertools module to efficiently
   generate all possible arrangements of digits for the multiplicand and multiplier.

3. For each valid pair, it calculates the product and checks if the combined digits of all three
   numbers form a 1-9 pandigital (i.e., they use each digit 1-9 exactly once).

4. The solution uses a set to ensure each product is counted only once, as required by the problem,
   before computing the final sum.

The implementation efficiently prunes the search space by only considering digit combinations
that could potentially form a valid pandigital product.

URL: https://projecteuler.net/problem=32
Answer: 45228
"""
from itertools import permutations

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=45228, ),
]

digits = ('1', '2', '3', '4', '5', '6', '7', '8', '9')


def sum_pandigital_products() -> int:
    """Calculate the sum of all products whose multiplicand/multiplier/product identity is 1-9 pandigital.

    A pandigital product identity is an equation a × b = c where the digits used in a, b, and c
    together use each digit from 1-9 exactly once.

    Returns:
        The sum of all unique products that can be written as part of a 1-9 pandigital identity

    Example:
        >>> sum_pandigital_products()
        45228  # Includes products like 7254 from 39 × 186
    """
    return sum(set(
        c
        for a_len, b_len in ((1, 4), (2, 3))
        for a in permutations(digits, a_len)
        for b in permutations((d for d in digits if d not in a), b_len)
        if ''.join(sorted((a_str := ''.join(a)) + (b_str := ''.join(b)) + str(c := (int(a_str) * int(b_str)))))
        == '123456789'))


# Create an alias for the sum_pandigital_products function to match the expected solution interface
# This allows the function to be named descriptively while still conforming to the
# Project Euler framework's convention of using 'solution' as the entry point
solution = sum_pandigital_products

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
