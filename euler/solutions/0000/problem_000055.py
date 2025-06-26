# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 55
# https://projecteuler.net/problem=55
# Answer: 249
# Notes: 
"""Solution to Project Euler problem 55: Lychrel numbers.

This module finds the count of Lychrel numbers below a given limit.

A Lychrel number is a number that never forms a palindrome through the
iteration process of reversing the digits and adding to the original number.

For example, 196 is considered a Lychrel number because it hasn't been proven
to eventually form a palindrome through this process, even after billions of iterations.

Key concepts:
- Palindromic numbers: Numbers that read the same forwards and backwards
- Reverse-and-add process: Adding a number to its digit-reversed form
- Lychrel numbers: Numbers that never produce palindromes through the reverse-and-add process
- Iteration limit: For this problem, a number is considered Lychrel if it doesn't
  form a palindrome within a specified number of iterations (typically 50)
"""
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test case for this problem
# For numbers below 10,000, using 50 iterations as the limit, there are 249 Lychrel numbers
problem_args_list: ProblemArgsList = [ProblemArgs(kwargs={'max_limit': 10000, 'max_iterations': 50}, answer=249, ), ]


def is_lychrel(*, number: int, max_iterations: int) -> bool:
    """Determine if a number is a Lychrel number.

    A Lychrel number is a number that never forms a palindrome through the iterative
    process of reversing its digits and adding to the original number. For the purpose
    of this problem, a number is considered Lychrel if it doesn't produce a palindrome
    within the specified maximum number of iterations.

    Args:
        number: The number to test for being a Lychrel number.
        max_iterations: The maximum number of reverse-and-add iterations to perform.

    Returns:
        True if the number is a Lychrel number (doesn't form a palindrome within
        the specified iterations), False otherwise.

    Examples:
        >>> is_lychrel(number=196, max_iterations=50)
        True  # 196 is thought to be a Lychrel number
        >>> is_lychrel(number=47, max_iterations=50)
        False  # 47 becomes palindromic after just one iteration
    """
    for _ in range(max_iterations):
        number += int(str(number)[::-1])
        if str(number) == str(number)[::-1]:
            return False
    else:
        return True


def solution(*, max_limit: int, max_iterations: int) -> int:
    """
    Count the number of Lychrel numbers below a given limit.

    This function counts how many Lychrel numbers exist below the specified limit.
    For each number from 1 to max_limit, it checks if it's a Lychrel number using
    the is_lychrel function and sums the results.

    The Problem Description from Project Euler:
    https://projecteuler.net/problem=55
    If we take 47, reverse and add, 47 + 74 = 121, which is palindromic.
    Not all numbers produce palindromes so quickly. For example,
        349 + 943 &= 1292
        1292 + 2921 &= 4213
        4213 + 3124 &= 7337
    That is, 349 took three iterations to arrive at a palindrome.
    Although no one has proved it yet, it is thought that some numbers, like 196, never produce a palindrome.
    A number that never forms a palindrome through the reverse and add process is called a Lychrel number.
    Due to the theoretical nature of these numbers, and for the purpose of this problem, we shall assume that
    a number is Lychrel until proven otherwise. In addition you are given that for every number below ten-thousand,
    it will either
        (i) become a palindrome in less than fifty iterations, or,
        (ii) no one, with all the computing power that exists, has managed so far to map it to a palindrome.
    In fact, 10677 is the first number to be shown to require over fifty iterations before producing a
    palindrome: 4668731596684224866951378664 (53 iterations, 28-digits).
    Surprisingly, there are palindromic numbers that are themselves Lychrel numbers; the first example is 4994.
    How many Lychrel numbers are there below ten-thousand?
    NOTE: Wording was modified slightly on 24 April 2007 to emphasise the theoretical nature of Lychrel numbers.

    Algorithm:
    1. Iterate through all numbers from 1 to max_limit
    2. For each number, check if it's a Lychrel number using the is_lychrel function
        - The is_lychrel function works by:
            a. Converting the number to a string and reversing its digits
            b. Adding the reversed number back to the original number
            c. Checking if the resulting sum is palindromic (reads same forwards and backwards)
            d. If palindromic, return False (not Lychrel)
            e. If not palindromic, repeat the process up to max_iterations
            f. If no palindrome is found within max_iterations, return True (is Lychrel)
    3. Count (the sum of True results) and return the total number of Lychrel numbers found

    Args:
        max_limit: The upper limit (exclusive) for finding Lychrel numbers
        max_iterations: The maximum number of reverse-and-add iterations to perform
                        before considering a number to be Lychrel

    Returns:
        The count of Lychrel numbers below max_limit

    Examples:
        >>> solution(max_limit=10000, max_iterations=50)
        249  # There are 249 Lychrel numbers below 10,000
    """
    return sum(is_lychrel(number=i, max_iterations=max_iterations) for i in range(1, max_limit + 1))


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
    evaluate_solution(solution=cast(SolutionProtocol, solution), args_list=problem_args_list, timeout=timeout,
                      max_workers=max_workers)
