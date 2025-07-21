# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 25: 1000-digit Fibonacci number

Problem Statement:
The Fibonacci sequence is defined by the recurrence relation:
F_n = F_{n-1} + F_{n-2}, where F_1 = 1 and F_2 = 1.

Hence the first 12 terms will be:
F_1 = 1
F_2 = 1
F_3 = 2
F_4 = 3
F_5 = 5
F_6 = 8
F_7 = 13
F_8 = 21
F_9 = 34
F_10 = 55
F_11 = 89
F_12 = 144

The 12th term, F_12, is the first term to contain three digits.
What is the index of the first term in the Fibonacci sequence to contain 1000 digits?

Solution Approach:
This implementation uses an iterative approach to generate Fibonacci numbers until reaching
the first number with the desired number of digits. The algorithm maintains only the two most
recent Fibonacci numbers in memory, making it memory-efficient. We determine the number of
digits by comparing each Fibonacci number with 10^(n-1), which is the smallest n-digit number.

Test Cases:
- For n=3, the answer is 12 (F_12 = 144 is the first 3-digit Fibonacci number)
- For n=1000, the answer is 4782

URL: https://projecteuler.net/problem=25
Answer: 4782
"""
from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=25)
problem_number: int = 25

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 3}, answer=12, ),
    ProblemArgs(kwargs={'n': 1000}, answer=4782, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def index_first_n_digit_fibonacci_number(*, n: int) -> int:
    """
    Find the index of the first Fibonacci number with n digits.

    This solution iteratively generates Fibonacci numbers using the recurrence relation
    F_n = F_{n-1} + F_{n-2}, starting with F_1 = F_2 = 1. It continues until finding the
    first number with at least n digits, determined by checking if the number is greater
    than or equal to 10^(n-1).

    Args:
        n: The number of digits to look for in a Fibonacci number

    Returns:
        The index (1-based) of the first Fibonacci number with n digits

    Example:
        >>> index_first_n_digit_fibonacci_number(n=3)
        12  # F_12 = 144 is the first Fibonacci number with 3 digits
        >>> index_first_n_digit_fibonacci_number(n=1000)
        4782  # The answer to the original problem
    """
    a, b = 1, 1
    i = 2
    while b < 10 ** (n - 1):
        a, b = b, a + b
        i += 1
    return i


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
