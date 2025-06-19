#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 47
# https://projecteuler.net/problem=47
# Answer: answers={2: 14, 3: 644, 4: 134043}
# Notes: 
"""Solution to Project Euler problem 47: Consecutive Prime Factors.

This module finds the first set of n consecutive integers, each having exactly n distinct
prime factors. The problem explores a pattern in number theory related to the distribution
of integers with specific prime factorization properties.

For example,
- When n=2: Find the first two consecutive integers with exactly 2 distinct prime factors each
- When n=3: Find the first three consecutive integers with exactly 3 distinct prime factors each
- When n=4: Find the first four consecutive integers with exactly 4 distinct prime factors each

The module uses an optimized approach that leverages the prime_factor_count function from
the euler.primes module, avoiding expensive repeated calculations through caching.

Key concepts:
- Prime factorization
- Consecutive integer sequences
- Number theory patterns
- Efficient sequence generation and testing
"""
import textwrap
from itertools import count

from euler.primes import prime_factor_count
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test cases for different values of n, demonstrating the pattern growth
# The answer values match those mentioned in the problem description
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'n': 2},  # First 2 consecutive integers with 2 distinct prime factors
        answer=14,        # 14=2×7 and 15=3×5
    ),
    ProblemArgs(
        kwargs={'n': 3},  # First 3 consecutive integers with 3 distinct prime factors
        answer=644,       # 644=2²×7×23, 645=3×5×43, 646=2×17×19
    ),
    ProblemArgs(
        kwargs={'n': 4},  # First 4 consecutive integers with 4 distinct prime factors
        answer=134043,    # The answer to the main problem
    ),
]


def solution(n: int) -> int:
    """
    Find the first of n consecutive integers, each with exactly n distinct prime factors.

    This function searches for the first occurrence of a sequence of n consecutive
    integers where each integer has exactly n distinct prime factors. It uses a
    generator expression with the itertools.count function to efficiently iterate
    through integers starting from 2 without creating large lists in memory.

    The algorithm:
    1. Iterate through consecutive integers starting from 2
    2. For each integer 'number', check if it and the next (n-1) consecutive integers
       all have exactly n distinct prime factors
    3. Return the first integer that satisfies this condition

    Args:
        n: The parameter defining both the length of the consecutive sequence and
           the number of distinct prime factors required for each integer

    Returns:
        The first integer in the sequence of n consecutive integers, each with
        exactly n distinct prime factors

    Examples:
        >>> solution(2)  # First of 2 consecutive integers with 2 distinct prime factors
        14              # 14=2×7 and 15=3×5
        >>> solution(3)  # First of 3 consecutive integers with 3 distinct prime factors
        644             # 644=2²×7×23, 645=3×5×43, 646=2×17×19
    """
    return next(number for number in count(2) if not any(prime_factor_count(number + i) != n for i in range(0, n)))


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 47: Distinct Primes Factors
https://projecteuler.net/problem=47

Problem Description:
The first two consecutive numbers to have two distinct prime factors are:
14 = 2 * 7
15 = 3 * 5.

The first three consecutive numbers to have three distinct prime factors are:
644 = 2^2 * 7 * 23
645 = 3 * 5 * 43
646 = 2 * 17 * 19.

Find the first four consecutive integers to have four distinct prime factors each. What is the first of these numbers?

Approach:
1. Efficient Prime Factor Counting:
   - We leverage the prime_factor_count function from euler.primes module
   - This function counts distinct prime factors (not including multiplicity)
   - The function uses wheel factorization and is optimized with LRU caching

2. Sequence Generation and Testing:
   - Use itertools.count to generate an infinite sequence of integers
   - For each integer n, check if n and the next three consecutive integers all have
     exactly 4 distinct prime factors
   - Return the first such integer found

3. Expression Optimization:
   - The solution uses a concise generator expression with the next() function
   - The any() function with a negation provides an elegant way to check if all
     consecutive integers have the required property

4. Pattern Generalization:
   - The solution generalizes to any value of n (not just 4)
   - We find n consecutive integers each with exactly n distinct prime factors
   - The problem becomes computationally more difficult as n increases

Mathematical Analysis:
- As n increases, the first occurrence of the pattern tends to grow rapidly:
  - For n=2: The answer is 14 (relatively small)
  - For n=3: The answer is 644 (about 46 times larger)
  - For n=4: The answer is 134043 (about 208 times larger)

- This rapid growth suggests that these configurations become increasingly rare
  as the number of required distinct prime factors increases

- The solution leverages the fact that the prime_factor_count function counts
  distinct prime factors (2³×3² has 2 distinct prime factors, not 5)

Time Complexity: O(m×sqrt(m)) where m is the answer value, as we need to factorize
numbers up to the answer, and factorization is roughly O(sqrt(n)) per number.

Space Complexity: O(log m) due to the call stack and temporary variables used in
the prime factorization process, plus additional memory used by the LRU cache.
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
