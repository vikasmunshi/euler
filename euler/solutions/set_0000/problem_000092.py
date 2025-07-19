#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 92:

Problem Statement:
A number chain is created by continuously adding the square of the digits in a number to form a new number until it has
been seen before.

For example,
44 -> 32 -> 13 -> 10 ->  1 ->  1
85 -> 89 -> 145 -> 42 -> 20 -> 4 -> 16 -> 37 -> 58 -> 89

Therefore any chain that arrives at 1 or 89 will become stuck in an endless loop. What is most amazing is that
EVERY starting number will eventually arrive at 1 or 89.

How many starting numbers below ten million will arrive at 89?

Solution Approach:
The solution uses a combinatorial approach for efficiency. Instead of checking each number individually, we:
1. Cache results using memoization to avoid redundant calculations
2. For larger inputs, use a digit-based combinatorial approach to count numbers that terminate at 89
3. For very large inputs, we can use mathematical properties to optimize further

Test Cases:
- max_num = 100: 80 numbers arrive at 89
- max_num = 10,000: 8,558 numbers arrive at 89
- max_num = 10,000,000: 8,581,146 numbers arrive at 89

URL: https://projecteuler.net/problem=92
Answer: 8581146 (for 10 million)
"""
from typing import Dict

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=92)
problem_number: int = 92

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'power_of_10': 2}, answer=80),
    ProblemArgs(kwargs={'power_of_10': 3}, answer=857),
    ProblemArgs(kwargs={'power_of_10': 4}, answer=8558),
    ProblemArgs(kwargs={'power_of_10': 5}, answer=85623),
    ProblemArgs(kwargs={'power_of_10': 6}, answer=856929),
    ProblemArgs(kwargs={'power_of_10': 7}, answer=8581146),
    ProblemArgs(kwargs={'power_of_10': 8}, answer=85744333),
    ProblemArgs(kwargs={'power_of_10': 9}, answer=854325192),
]


def terminates_in_89(n: int) -> bool:
    """Check if a number eventually leads to 89 in the digit square sum chain.

    This function calculates the sum of squares of digits repeatedly until
    the sequence reaches either 1 or 89, which are the only two possible
    terminal states for any starting number.

    Args:
        n: The number to check

    Returns:
        True if the number terminates at 89, False if it terminates at 1
    """
    while n != 1 and n != 89:
        n, t = 0, n
        while t:
            n, t = n + (t % 10) ** 2, t // 10
    return n == 89


# Register this function as a solution for problem #92 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def square_of_digits_number_chain(*, power_of_10: int) -> int:
    """
    Count how many numbers below 10^power_of_10 will arrive at 89 in their digit square sum chain.

    This function uses a combinatorial approach for efficiency. Instead of checking each number
    individually (which would be too slow for large inputs like 10^7), it uses the following approach:

    1. We track how many numbers can be formed with specific digit square sums
    2. We build this count progressively for each order of magnitude
    3. We maintain a list of which sums terminate in 89
    4. For each iteration, we expand our counts based on the possible digit combinations

    The algorithm leverages the fact that the maximum sum of squares for a 7-digit number is
    9²×7 = 567, which means we only need to track a limited set of possible sums.

    Args:
        power_of_10: Calculate for numbers below 10^power_of_10

    Returns:
        Count of numbers below 10^power_of_10 that terminate at 89
    """
    # a[i] represents how many numbers with digit square sum = i we've seen so far
    # sq contains all possible squares of single digits (1-9)
    # is89 tracks which sums terminate at 89
    a, sq, is89 = [1], [x ** 2 for x in range(1, 10)], [False]
    results: Dict[int, int] = {}

    for n in range(1, power_of_10 + 1):
        # Save current counts in b, then extend a for the next magnitude
        # We need 81 more positions because adding a digit can increase sum by at most 9² = 81
        b, a = a, a + [0] * 81

        # Determine which new sums terminate at 89 and add to our tracker
        is89 += map(terminates_in_89, range(len(b), len(a)))

        # For each existing sum (i) and its count (v), distribute to new sums
        # by adding each possible digit square (s)
        for i, v in enumerate(b):
            for s in sq:
                a[i + s] += v

        # Count all numbers that terminate at 89 for this magnitude
        results[n] = sum(a[i] for i in range(len(a)) if is89[i])

    if show_solution():
        print(f'Results for power_of_10={power_of_10}: {results}')
    return results[power_of_10]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
