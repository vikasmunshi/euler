#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 43
# https://projecteuler.net/problem=43
# Answer: 16695334890
# Notes: 
"""Solution to Project Euler problem 43: Sub-string divisibility.

This module solves the problem of finding the sum of all 0 to 9 pandigital numbers
with a specific sub-string divisibility property, where consecutive three-digit
substrings are divisible by specific prime numbers.

The solution uses Python's itertools.permutations to generate all possible
10-digit pandigital numbers and then filters them based on the divisibility
requirements specified in the problem.

Key concepts:
- Pandigital numbers (containing all digits 0-9)
- Modular arithmetic (divisibility tests)
- Combinatorial generation (permutations)
- Functional programming techniques (list comprehensions, generators)
"""
import textwrap
from itertools import permutations
from typing import Tuple

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# List of test cases for this problem
# For this problem, no additional input parameters are needed
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},  # No input parameters required
        answer=16695334890,  # The expected sum of all matching pandigital numbers
    ),
]


def solution() -> int:
    """Calculate the sum of all 0-9 pandigital numbers with specific divisibility properties.

    This function:
    1. Generates all possible permutations of digits 0-9
    2. Filters out permutations that start with 0 (not 10-digit numbers)
    3. Checks each permutation for the required divisibility properties:
       - d₂d₃d₄ is divisible by 2
       - d₃d₄d₅ is divisible by 3
       - d₄d₅d₆ is divisible by 5
       - d₅d₆d₇ is divisible by 7
       - d₆d₇d₈ is divisible by 11
       - d₇d₈d₉ is divisible by 13
       - d₈d₉d₁₀ is divisible by 17
    4. Sums all numbers that satisfy these conditions

    Returns:
        The sum of all matching pandigital numbers
    """
    divisors: Tuple[int, int, int, int, int, int, int] = (2, 3, 5, 7, 11, 13, 17)
    return sum(int(''.join(num_s)) for num_s in permutations('0123456789')
               if num_s[0] != '0'  # Skip numbers starting with 0
               and not any(int(''.join(num_s[i:i + 3])) % divisor != 0 for i, divisor in enumerate(divisors, start=1)))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 43: Sub-string divisibility
https://projecteuler.net/problem=43

Problem Description:
The number, 1406357289, is a 0 to 9 pandigital number because it is made up of each of the digits 0 to 9 in some order,
but it also has a rather interesting sub-string divisibility property.
Let d_1 be the 1st digit, d_2 be the 2nd digit, and so on. In this way, we note the following:
d_2d_3d_4=406 is divisible by 2
d_3d_4d_5=063 is divisible by 3
d_4d_5d_6=635 is divisible by 5
d_5d_6d_7=357 is divisible by 7
d_6d_7d_8=572 is divisible by 11
d_7d_8d_9=728 is divisible by 13
d_8d_9d_10=289 is divisible by 17
Find the sum of all 0 to 9 pandigital numbers with this property.

Approach:
1. Generate all possible permutations of the digits 0-9.
   - Python's itertools.permutations is used for efficient generation.

2. Filter candidates by applying two conditions:
   a. The number should not start with 0 (to maintain 10 digits).
   b. Each 3-digit substring must be divisible by the corresponding prime in our list.

3. For each valid permutation, convert it to an integer and add it to our running sum.

Optimizations:
- The solution uses a generator expression to avoid storing all permutations in memory.
- The any() function short-circuits evaluation as soon as any divisibility test fails.
- We use string joining and direct integer conversion for clarity and performance.
- The divisibility check uses a clever combination of enumerate with start=1 to match
  the 1-indexed nature of the digit positions in the problem description.

Mathematical Insights:
- The number of permutations of 10 digits is 10! = 3,628,800, which is manageable for
  a modern computer to check exhaustively.
- Each divisibility constraint reduces the search space significantly.
- The prime divisors (2, 3, 5, 7, 11, 13, 17) were specifically chosen to provide
  strong filtering properties.

Time Complexity: O(n!) where n=10, dominated by generating all permutations.
Space Complexity: O(n) for storing each permutation during processing.
''').strip()

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
