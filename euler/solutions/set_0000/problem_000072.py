# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Solution to Project Euler problem 72: Counting Reduced Proper Fractions

Problem Statement:
Consider the fraction, n/d, where n and d are positive integers. If n < d and HCF(n,d)=1,
it is called a reduced proper fraction.

If we list the set of reduced proper fractions for d < 8 in ascending order of size, we get:
1/8, 1/7, 1/6, 1/5, 1/4, 2/7, 1/3, 3/8, 2/5, 3/7, 1/2, 4/7, 3/5, 5/8, 2/3, 5/7, 3/4, 4/5, 5/6, 6/7, 7/8

It can be seen that there are 21 elements in this set.

How many elements would be contained in the set of reduced proper fractions for d < 1 000 000?

Solution Approach:
This problem is essentially asking for the sum of Euler's totient function φ(n) for n from 2 to 999,999.
The totient function φ(n) counts the number of integers up to n that are coprime to n.
We use a sieve-based approach to efficiently calculate the totient values for all numbers up to max_d.

Test Cases:
- For d < 8: 21 elements
- For d < 10: 31 elements
- For d < 100: 3043 elements
- For d < 1000: 304191 elements

URL: https://projecteuler.net/problem=72
Answer: 30396356427241
"""
from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=72)
problem_number: int = 72

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_d': 8}, answer=21, ),
    ProblemArgs(kwargs={'max_d': 10 ** 1}, answer=31, ),
    ProblemArgs(kwargs={'max_d': 10 ** 2}, answer=3043, ),
    ProblemArgs(kwargs={'max_d': 10 ** 3}, answer=304191, ),
    ProblemArgs(kwargs={'max_d': 10 ** 4}, answer=30397485, ),
    ProblemArgs(kwargs={'max_d': 10 ** 5}, answer=3039650753, ),
    ProblemArgs(kwargs={'max_d': 10 ** 6}, answer=303963552391, ),
    ProblemArgs(kwargs={'max_d': 10 ** 7}, answer=30396356427241, ),
]


# Register this function as a solution for problem #72 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def number_of_reduced_fractions(*, max_d: int) -> int:
    """
    Calculate the total number of reduced proper fractions for denominators less than max_d.

    Args:
        max_d: The upper limit for denominators (exclusive)

    Returns:
        The count of all reduced proper fractions with denominators less than max_d
    """
    # Initialize the totient array with values from 0 to max_d
    # Each number starts as its own value before applying Euler's totient function
    euler_totients: List[int] = list(range(max_d + 1))

    # Apply the sieve method to calculate totients
    # For each prime p, multiply numbers containing p by (p-1)/p
    for n in range(2, max_d + 1):
        if euler_totients[n] == n:  # n is prime (unchanged from the initial value)
            for j in range(n, max_d + 1, n):
                # Update totient: multiply by (p-1)/p for each prime factor
                euler_totients[j] = (euler_totients[j] // n) * (n - 1)
    return sum(euler_totients[d] for d in range(2, max_d + 1))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
