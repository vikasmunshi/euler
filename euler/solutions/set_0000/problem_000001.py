#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 1: Multiples of 3 and 5

Problem Statement:
If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9.
The sum of these multiples is 23.
Find the sum of all the multiples of 3 or 5 below 1000.

Solution Approach:
This implementation uses a mathematical optimization based on the arithmetic sum formula
rather than iterating through each number. By applying the inclusion-exclusion principle,
we avoid double-counting numbers that are multiples of both 3 and 5.

The formula used is:
Sum = Sum of multiples of 3 + Sum of multiples of 5 - Sum of multiples of 15

For each term, we use the arithmetic series sum formula: n(n+1)/2 * d,
where n is the count of terms and d is the common difference (3, 5, or 15).

Test Cases:
- For max_limit=10, the answer is 23
- For max_limit=1000, the answer is 233,168

URL: https://projecteuler.net/problem=1
Answer: 233,168
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=1)
problem_number: int = 1

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_limit': 10}, answer=23, ),  # Example case from the problem statement
    ProblemArgs(kwargs={'max_limit': 1000}, answer=233168, ),  # Actual problem case
]


# Register this function as a solution for problem #1 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def multiples_of_3_and_5(*, max_limit: int) -> int:
    """
    This solution uses the arithmetic sum formula to efficiently calculate
    the sum of multiples without iterating through each number. It applies
    the inclusion-exclusion principle to avoid double-counting numbers that
    are multiples of both 3 and 5 (i.e., multiples of 15).

    Args:
        max_limit: An integer representing the upper bound (exclusive)

    Returns:
        The sum of all multiples of 3 or 5 below max_limit

    Example:
        >>> multiples_of_3_and_5(max_limit=10)
        23
        >>> multiples_of_3_and_5(max_limit=1000)
        233,168
    """

    def sum_multiples(number: int) -> int:
        """Calculate the sum of multiples of 'number' up-to max_limit using formula for arithmetic sum: n(n+1)/2."""
        terms = (max_limit - 1) // number
        return number * terms * (terms + 1) // 2

    # Apply inclusion-exclusion principle:
    # sum(multiples of 3) + sum(multiples of 5) - sum(multiples of 15)
    return sum_multiples(3) + sum_multiples(5) - sum_multiples(3 * 5)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
