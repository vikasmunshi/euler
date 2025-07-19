#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 100:

Problem Statement:
If a box contains twenty-one coloured discs, composed of fifteen blue discs and six red discs,
and two discs were taken at random, it can be seen that the probability of taking two blue discs,
P(BB) = (15/21) × (14/20) = 1/2.

The next such arrangement, for which there is exactly 50% chance of taking two blue discs at random,
is a box containing eighty-five blue discs and thirty-five red discs.

By finding the first arrangement to contain over 10^12 = 1000000000000 discs in total,
determine the number of blue discs that the box would contain.

Solution Approach:
For a probability of 1/2 when drawing two blue discs, we need:
b/n * (b-1)/(n-1) = 1/2

This can be rewritten as: 2b(b-1) = n(n-1)
Expanding: 2b² - 2b = n² - n
Rearranging: 2b² - 2b - n² + n = 0

This is a Diophantine equation. We can solve it by rewriting it in terms of:
2b - 1 = y and 2n - 1 = x

Substituting and simplifying, we get: y² - 2x² = -1

This is a negative Pell equation. We can find solutions using recurrence relations
based on the fundamental solution (x₁, y₁) = (1, 1):
x_{k+1} = x₁x_k + 2y₁y_k
y_{k+1} = y₁x_k + x₁y_k

Then we compute n and b from x and y:
n = (x + 1) / 2
b = (y + 1) / 2

Test Cases:
- For n = 21, b = 15 (first example)
- For n = 120, b = 85 (second example)
- For n > 10^12, b = 756872327473 (answer)

URL: https://projecteuler.net/problem=100
Answer: 756872327473
"""

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=100)
problem_number: int = 100

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'total_discs': 21}, answer=15, ),
    ProblemArgs(kwargs={'total_discs': 120}, answer=85, ),
    ProblemArgs(kwargs={'total_discs': 10 ** 12}, answer=756872327473, ),
]


# Register this function as a solution for problem #100 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def num_blue_discs_pell_method(*, total_discs: int) -> int:
    """
    Calculate the number of blue discs needed for a probability of 1/2 when drawing two blue discs.

    The problem requires solving the equation: b/n * (b-1)/(n-1) = 1/2
    This can be transformed into a negative Pell equation: y² - 2x² = -1
    where y = 2b - 1 and x = 2n - 1

    Args:
        total_discs: The minimum total number of discs required

    Returns:
        The number of blue discs in the first valid arrangement with at least total_discs discs
    """
    # Initial solution to the negative Pell equation y² - 2x² = -1
    x, y = 1, 1
    # Generate solutions using recurrence relations
    while True:
        # Calculate next solution using recurrence formula
        x, y = 3 * x + 4 * y, 2 * x + 3 * y

        # Convert back to n and b
        n = (x + 1) // 2
        b = (y + 1) // 2

        # Check if we found a solution with total_discs > 10^12
        if n >= total_discs:
            return b


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
