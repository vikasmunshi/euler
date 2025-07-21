# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 6: Sum Square Difference

Problem Statement:
The sum of the squares of the first ten natural numbers is,
1² + 2² + ... + 10² = 385.

The square of the sum of the first ten natural numbers is,
(1 + 2 + ... + 10)² = 55² = 3025.

Hence the difference between the sum of the squares of the first ten natural numbers
and the square of the sum is 3025 - 385 = 2640.

Find the difference between the sum of the squares of the first one hundred natural
numbers and the square of the sum.

Solution Approach:
This problem can be solved using mathematical formulas rather than explicit computation:

1. Sum of first n natural numbers: n(n+1)/2
   This is a well-known formula attributed to Gauss

2. Sum of squares of first n natural numbers: n(n+1)(2n+1)/6
   This is a standard mathematical formula derived from sequence analysis

3. The difference is calculated by:
   [Sum of first n natural numbers]² - [Sum of squares of first n natural numbers]
   = [n(n+1)/2]² - n(n+1)(2n+1)/6

Using these formulas allows us to compute the result in O(1) time complexity
regardless of the input size, which is much more efficient than using loops.

Test Cases:
- For n=10: 2640
- For n=100: 25164150

URL: https://projecteuler.net/problem=6
Answer: 25164150
"""
from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=6)
problem_number: int = 6

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 10}, answer=2640, ),  # Test case where n=10 Expected answer for n=10
    ProblemArgs(kwargs={'n': 100}, answer=25164150, ),  # Test case where n=100 Expected answer for n=100
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def square_of_sum_minus_sum_of_squares(*, n: int) -> int:
    """
    Computes the difference between the square of the sum of the first `n`
    natural numbers and the sum of the squares of the first `n` natural numbers.

    Args:
        n (int): The number up to which the calculations are performed.

    Returns:
        int: The difference between the square of the sum and the sum of the squares.

    Explanation:
    - The sum of the first `n` natural numbers is calculated as:
      S = (n * (n + 1) // 2)
    - The square of the sum is:
      S^2
    - The sum of the squares of the first `n` natural numbers is calculated as:
      Sum of squares = (2 * n + 1) * (n + 1) * n // 6
    - Finally, the difference is:
      S^2 - Sum of squares
    """
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
