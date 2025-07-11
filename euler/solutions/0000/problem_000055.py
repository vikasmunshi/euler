#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 55: Lychrel Numbers

Problem Statement:
If we take 47, reverse and add, 47 + 74 = 121, which is palindromic.
Not all numbers produce palindromes so quickly. For example,
349 + 943 = 1292
1292 + 2921 = 4213
4213 + 3124 = 7337

That is, 349 took three iterations to arrive at a palindrome.
Although no one has proved it yet, it is thought that some numbers, like 196, never produce a palindrome. 
A number that never forms a palindrome through the reverse and add process is called a Lychrel number. 
Due to the theoretical nature of these numbers, and for the purpose of this problem, we shall assume that 
a number is Lychrel until proven otherwise. In addition you are given that for every number below ten-thousand, 
it will either (i) become a palindrome in less than fifty iterations, or, (ii) no one, with all the computing 
power that exists, has managed so far to map it to a palindrome. In fact, 10677 is the first number to be shown 
to require over fifty iterations before producing a palindrome: 4668731596684224866951378664 (53 iterations, 28-digits).

Surprisingly, there are palindromic numbers that are themselves Lychrel numbers; the first example is 4994.

How many Lychrel numbers are there below ten-thousand?

Solution Approach:
The solution implements a straightforward approach to identify Lychrel numbers:

1. For each number from 1 to 10,000, apply the reverse-and-add process up to 50 times
2. If the resulting number becomes a palindrome (reads the same forwards and backwards), it's not a Lychrel number
3. If after 50 iterations no palindrome is found, consider it a Lychrel number
4. Count the total number of Lychrel numbers found

Test Cases:
- For max_limit=10000, max_iterations=50: 249 Lychrel numbers found

URL: https://projecteuler.net/problem=55
Answer: 249
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_limit': 10000, 'max_iterations': 50}, answer=249, ),
]


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

    This solution identifies Lychrel numbers by applying the reverse-and-add process for each
    number from 1 to max_limit. If a number doesn't form a palindrome within max_iterations,
    it is considered a Lychrel number for the purpose of this problem.

    Args:
        max_limit: The upper limit (inclusive) for finding Lychrel numbers
        max_iterations: The maximum number of reverse-and-add iterations to perform
                        before considering a number to be Lychrel

    Returns:
        The count of Lychrel numbers below max_limit

    Example:
        >>> solution(max_limit=10000, max_iterations=50)
        249
    """
    return sum(is_lychrel(number=i, max_iterations=max_iterations) for i in range(1, max_limit + 1))


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
