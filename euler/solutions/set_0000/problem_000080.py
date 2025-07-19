# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 80:

Problem Statement:
It is well known that if the square root of a natural number is not an integer, then it is irrational.
The decimal expansion of such square roots is infinite without any repeating pattern at all.

The square root of two is 1.41421356237309504880·s, and the digital sum of the first one hundred decimal digits is 475.

For the first one hundred natural numbers, find the total of the digital sums of the first one hundred decimal digits
for all the irrational square roots.

Solution Approach:
1. Use either Heron's method (Newton's method) or binary search to calculate square roots with high precision
2. For each number from 2 to the maximum specified (default 99):
   a. Skip perfect squares as they have terminating decimal expansions
   b. Calculate the square root with the required number of decimal digits
   c. Sum the digits of the square root and add to the running total
3. Return the total sum of all digits across all irrational square roots

Implementation Methods:

1. Heron's Method (sqrt_heron_method):
   - Multiply the original number by 10^(2*digits) to get enough precision
   - Apply the iterative formula: x_(n+1) = (x_n + number/x_n) / 2
   - Continue until convergence (when x_n = x_(n+1))
   - Take the first 'digits' digits of the result
   - Faster convergence but may vary in performance based on input values

2. Binary Search Method (sqrt_binary_search):
   - Multiply the original number by 10^(2*digits) to get enough precision
   - Use binary search to find the square root with the specified precision
   - More predictable performance characteristics across different inputs
   - Generally slower than Heron's method but more consistent

Test Cases:
- For max_num=2 and digits=100: Expected sum is 475 (verified with √2)
- For max_num=99 and digits=100: Expected sum is 40886
- For max_num=999 and digits=100: Expected sum is 434576

URL: https://projecteuler.net/problem=80
Answer: 40886
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.misc import sum_digits
from euler.utils.sqrt import sqrt_binary_search, sqrt_heron_method

# The problem number from Project Euler (https://projecteuler.net/problem=80)
problem_number: int = 80

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_num': 2, 'digits': 100}, answer=475, ),
    ProblemArgs(kwargs={'max_num': 99, 'digits': 100}, answer=40886, ),
    ProblemArgs(kwargs={'max_num': 999, 'digits': 100}, answer=434576, ),
]


# Register this function as a solution for problem #80 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_irrational_sqrt_digits_heron_method(*, max_num: int, digits: int) -> int:
    """Calculate the sum of digits for irrational square roots using Heron's method.

    This function calculates the sum of the first 'digits' decimal digits
    for the square roots of all non-perfect-square numbers from 2 to max_num.
    It uses the Heron's method implementation from the euler.utils.sqrt module.

    Args:
        max_num: The maximum number to consider (inclusive)
        digits: The number of decimal digits to include in the calculation

    Returns:
        The sum of all digits across all irrational square roots

    Example:
        For max_num=2 and digits=100, the function returns 475, which is
        the sum of the first 100 digits of the square root of 2.

    Performance:
        Heron's method typically converges quickly and is efficient for most inputs,
        making it the preferred implementation for this problem.
    """
    result: int = 0
    for i in range(2, max_num + 1):
        if (i ** 0.5) % 1 == 0:  # is a perfect square
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
    return result


# Register this function as a solution for problem #80 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_irrational_sqrt_digits_binary_search(*, max_num: int, digits: int) -> int:
    """Calculate the sum of digits for irrational square roots using binary search.

    This function calculates the sum of the first 'digits' decimal digits
    for the square roots of all non-perfect-square numbers from 2 to max_num.
    It uses the binary search implementation from the euler.utils.sqrt module.

    Args:
        max_num: The maximum number to consider (inclusive)
        digits: The number of decimal digits to include in the calculation

    Returns:
        The sum of all digits across all irrational square roots

    Example:
        For max_num=2 and digits=100, the function returns 475, which is
        the sum of the first 100 digits of the square root of 2.

    Performance:
        The binary search method provides more consistent performance across
        different inputs compared to Heron's method, but is generally slower.
        It's included as an alternative implementation for validation and
        comparison purposes.
    """
    result: int = 0
    for i in range(2, max_num + 1):
        if (i ** 0.5) % 1 == 0:  # is a perfect square
            continue
        result += sum_digits(sqrt_binary_search(i, digits))
    return result


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
