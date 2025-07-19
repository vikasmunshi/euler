# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution to Project Euler problem 73.

Problem Statement:
    Consider the fraction, n/d, where n and d are positive integers. If n < d and
    HCF(n,d)=1, it is called a reduced proper fraction.

    If we list the set of reduced proper fractions for d ≤ 8 in ascending order of size:
    1/8, 1/7, 1/6, 1/5, 1/4, 2/7, 1/3, 3/8, 2/5, 3/7, 1/2, 4/7, 3/5, 5/8, 2/3,
    5/7, 3/4, 4/5, 5/6, 6/7, 7/8

    It can be seen that there are 3 fractions between 1/3 and 1/2.

    How many fractions lie between 1/3 and 1/2 in the sorted set of reduced proper
    fractions for d ≤ 12,000?

Solution Approach:
    This module provides three different approaches to solve the problem:

    1. Recursive Solution (count_fractions_within_range_recursion):
       Uses the Farey sequence property to recursively generate and count mediants
       between 1/3 and 1/2. The mediant of two fractions a/b and c/d is (a+c)/(b+d).

    2. Iterative Solution (count_fractions_within_range_iteration):
       Implements an iterative version of the Farey sequence generation, avoiding
       recursion stack limitations for large denominators. It uses a formula to
       calculate the next denominator in the sequence.

    3. Rank-based Solution (count_fractions_within_range_rank):
       Uses a more efficient approach based on counting numbers using arithmetic
       progressions and sieve-like techniques. This method is the fastest and can
       handle larger inputs.

URL: https://projecteuler.net/problem=73
Answer: 7295372
"""
from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.sys_utils import set_resource_limits
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=73)
problem_number: int = 73

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_d': 8}, answer=3, ),
    ProblemArgs(kwargs={'max_d': 1000}, answer=50695, ),
    ProblemArgs(kwargs={'max_d': 12000}, answer=7295372, ),
    ProblemArgs(kwargs={'max_d': 100000}, answer=506608484, ),
]


# Register this function as a solution for problem #73 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list[:-2])
@set_resource_limits(recursion_var='max_d', multiplier=1, set_int_max_str=False, when='always')
def count_fractions_within_range_recursion(*, max_d: int) -> int:
    """Count fractions between 1/3 and 1/2 using recursive Farey sequence.

    Args:
        max_d: Maximum denominator value to consider.

    Returns:
        Number of reduced proper fractions between 1/3 and 1/2.
    """

    def recursion(lower_denominator: int, upper_denominator: int) -> int:
        # Check if the denominator exceeds the maximum allowed
        if (mediant := lower_denominator + upper_denominator) > max_d:
            return 0
        # Recursively count mediants
        return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)

    return recursion(lower_denominator=3, upper_denominator=2)


# Register this function as a solution for problem #73 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list[:-1])
def count_fractions_within_range_iteration(*, max_d: int) -> int:
    """Count fractions between 1/3 and 1/2 using iterative approach.

    Args:
        max_d: Maximum denominator value to consider.

    Returns:
        Number of reduced proper fractions between 1/3 and 1/2.
    """
    lower_denominator: int = 3
    upper_denominator: int = 2
    # initial mediant closest to lower_denominator
    d = upper_denominator + lower_denominator * ((max_d - upper_denominator) // lower_denominator)
    # If `prev_d` and `d` are denominators of adjacent fractions
    # prev_n/prev_d and n/d, then the next denominator is:
    # max_d - (max_d + prev_d) % d
    prev_d = lower_denominator
    count = 0
    # Until we reach the final denominator
    while d != upper_denominator:
        count += 1
        # Shift: the current becomes the previous
        prev_d, d = d, max_d - (max_d + prev_d) % d
    return count


# Register this function as a solution for problem #73 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def count_fractions_within_range_rank(max_d: int) -> int:
    """Count fractions between 1/3 and 1/2 using a rank-based arithmetic approach.

    Args:
        max_d: Maximum denominator value to consider.

    Returns:
        Number of reduced proper fractions between 1/3 and 1/2.
    """

    def rank(n: int, d: int) -> int:
        len_data: int = max_d + 1
        # Initialize the data array
        data: List[int] = [i * n // d for i in range(len_data)]
        # Remove all multiples (similar to sieve of Eratosthenes)
        for i in range(1, len_data):
            for j in range(2 * i, len_data, i):
                data[j] -= data[i]
        # Return the sum of all elements in the data array
        return sum(data)

    return rank(n=1, d=2) - rank(n=1, d=3) - 1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
