#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 92: square_digit_chains

Problem Statement:
  A number chain is created by continuously adding the square of the digits in a
  number to form a new number until it has been seen before. For example,
  \begin{align} &44 \to 32 \to 13 \to 10 \to \mathbf 1 \to \mathbf 1\\ &85 \to
  \mathbf{89} \to 145 \to 42 \to 20 \to 4 \to 16 \to 37 \to 58 \to \mathbf{89}
  \end{align} Therefore any chain that arrives at 1 or 89 will become stuck in an
  endless loop. What is most amazing is that EVERY starting number will eventually
  arrive at 1 or 89. How many starting numbers below ten million will arrive at
  89?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=92
Answer: None
"""
from __future__ import annotations

from typing import Dict

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=80,
        is_main_case=False,
        kwargs={'power_of_10': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=857,
        is_main_case=False,
        kwargs={'power_of_10': 3},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=8558,
        is_main_case=False,
        kwargs={'power_of_10': 4},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=85623,
        is_main_case=False,
        kwargs={'power_of_10': 5},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=856929,
        is_main_case=False,
        kwargs={'power_of_10': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=8581146,
        is_main_case=False,
        kwargs={'power_of_10': 7},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=85744333,
        is_main_case=False,
        kwargs={'power_of_10': 8},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=854325192,
        is_main_case=False,
        kwargs={'power_of_10': 9},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #92
@register_solution(problem_number=92, test_cases=test_cases)
def square_digit_chains(*, power_of_10: int) -> int:
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


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(92))
