#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 40
# https://projecteuler.net/problem=40
# Answer: 210
# Notes: 
"""
Solution to Project Euler problem 40 - Champernowne's constant.

This module provides functions to work with Champernowne's constant,
an irrational decimal fraction created by concatenating positive integers:
0.12345678910111213...

The main solution calculates the product of digits at specific positions
(1, 10, 100, etc.) in this constant.

Functions:
    get_nth_digit_champernowne_s_constant: Find the nth digit in Champernowne's constant
    solution: Calculate the product of digits at positions 10^0 through 10^i
"""
import textwrap
from functools import reduce

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'i': 1}, answer=1, ),
    ProblemArgs(kwargs={'i': 2}, answer=5, ),
    ProblemArgs(kwargs={'i': 3}, answer=15, ),
    ProblemArgs(kwargs={'i': 4}, answer=105, ),
    ProblemArgs(kwargs={'i': 5}, answer=210, ),
    ProblemArgs(kwargs={'i': 6}, answer=210, ),
    ProblemArgs(kwargs={'i': 7}, answer=1470, ),
    ProblemArgs(kwargs={'i': 8}, answer=11760, ),
    ProblemArgs(kwargs={'i': 9}, answer=11760, ),
    ProblemArgs(kwargs={'i': 10}, answer=11760, ),
    ProblemArgs(kwargs={'i': 11}, answer=0, ),
]


def get_nth_digit_champernowne_s_constant(n: int) -> int:
    """
    Calculate the nth digit of Champernowne's constant.

    Champernowne's constant is formed by concatenating positive integers:
    0.12345678910111213...

    Parameters:
        n: The position of the digit to find (1-indexed)

    Returns:
        The digit at the nth position as an integer

    Algorithm:
    1. Determine how many digits the number containing the nth digit has
    2. Calculate the specific number that contains the nth digit
    3. Extract the correct digit from that number

    Example:
        For n=12, the function returns 1 (the 12th digit in the sequence is 1)
    """
    length_till_num_digits, length_with_num_digits, num_digits = 0, 0, 0
    while length_with_num_digits < n:
        num_digits += 1
        length_till_num_digits = length_with_num_digits
        length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)

    offset_of_number = n - length_till_num_digits - 1
    digit_in_number = offset_of_number % num_digits
    number = 10 ** (num_digits - 1) + offset_of_number // num_digits
    return int(str(number)[digit_in_number])


def solution(*, i: int) -> int:
    """
    Calculate the product of specific digits in Champernowne's constant.

    This function finds the product of digits at positions 1, 10, 100, ..., 10^i
    in Champernowne's constant (0.12345678910111213...).

    Parameters:
        i: The maximum exponent to consider (inclusive)
           The function will calculate the product of digits at positions
           10^0, 10^1, 10^2, ..., 10^i

    Returns:
        The product of the digits at the specified positions

    Example:
        For i=6, the function returns the product of the digits at positions
        1, 10, 100, 1000, 10,000, 100,000, and 1,000,000
    """
    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10 ** i) for i in range(0, i + 1)), 1)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 40
https://projecteuler.net/problem=40
An irrational decimal fraction is created by concatenating the positive integers:
0.12345678910 112131415161718192021...
It can be seen that the 12th digit of the fractional part is 1.
If d_n represents the nth digit of the fractional part, find the value of the following expression.
d_1 * d_{10} * d_{100} * d_{1000} * d_{10000} * d_{100000} * d_{1000000}

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
