#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 21
# https://projecteuler.net/problem=21
# Answer: answers={10000: 31626}
# Notes: This solution efficiently computes amicable numbers using an optimized factor sum function with memoization.
import textwrap
from functools import lru_cache

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    # Test case for finding the sum of all amicable numbers under 10,000
    # The expected answer (31,626) is the sum of all amicable numbers: 220, 284, 1184, 1210, etc. under 10,000
    ProblemArgs(
        kwargs={'max_num': 10000},
        answer=31626,
    ),
]


@lru_cache()
def sum_factors(n: int) -> int:
    """Calculate the sum of proper divisors (factors) of n.

    This optimized implementation finds all divisors by iterating only up to the square root of n.
    For each divisor i, we also include n//i as a divisor, avoiding duplicate counting of perfect squares.
    The function returns the sum of all proper divisors (excluding n itself).

    Args:
        n: A positive integer

    Returns:
        The sum of all proper divisors of n
    """
    n_sqrt = int(n ** 0.5)
    return 1 + sum(i + n // i for i in range(2, n_sqrt + 1) if n % i == 0) - (n_sqrt if n_sqrt ** 2 == n else 0)


def solution(*, max_num: int) -> int:
    """Find the sum of all amicable numbers under max_num.

    An amicable number pair (a,b) exists when sum_factors(a) = b and sum_factors(b) = a,
    where a ≠ b. This function checks each number up to max_num, computes its proper
    divisor sum (d(x)), and checks if d(d(x)) = x while ensuring x ≠ d(x) to avoid
    perfect numbers (which are not amicable numbers).

    The @lru_cache decorator on sum_factors significantly improves performance by
    memoizing the results of previous calculations.

    Args:
        max_num: Upper limit for finding amicable numbers

    Returns:
        Sum of all amicable numbers below max_num
    """
    return sum(x for x in range(2, max_num + 1) if (y := sum_factors(x)) != x and sum_factors(y) == x)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 21: Amicable Numbers
https://projecteuler.net/problem=21

Problem Statement:
Let d(n) be defined as the sum of proper divisors of n (numbers less than n which divide evenly into n).

If d(a) = b and d(b) = a, where a ≠ b, then a and b are an amicable pair and each of a and b are called amicable numbers.
For example, the proper divisors of 220 are 1, 2, 4, 5, 10, 11, 20, 22, 44, 55 and 110; therefore d(220) = 284.
The proper divisors of 284 are 1, 2, 4, 71 and 142; so d(284) = 220.

Task: Evaluate the sum of all the amicable numbers under 10000.

Solution Approach:
1. Define an efficient function to calculate the sum of proper divisors (sum_factors)
2. Use memoization via @lru_cache to avoid recalculating divisor sums
3. For each number x from 2 to max_num:
   - Calculate y = sum_factors(x)
   - Check if sum_factors(y) = x and x ≠ y
   - If true, x is an amicable number
4. Return the sum of all identified amicable numbers

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
