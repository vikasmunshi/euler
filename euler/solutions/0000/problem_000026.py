#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 26: Reciprocal cycles
# https://projecteuler.net/problem=26
# Answer: 983
# Notes: This solution uses number theory to find the longest recurring decimal cycle
#        by calculating the multiplicative order of 10 modulo d.
import textwrap
from math import gcd
from typing import Optional

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_val': 10},
        answer=7,
    ),
    ProblemArgs(
        kwargs={'max_val': 100},
        answer=97,
    ),
    ProblemArgs(
        kwargs={'max_val': 1000},
        answer=983,
    ),
]


def multiplicative_order(a: int, modulus: int) -> Optional[int]:
    """
    Calculate the multiplicative order of a modulo modulus.

    The multiplicative order is the smallest positive integer k such that a^k ≡ 1 (mod modulus).
    For decimal fractions 1/d, the length of the recurring cycle equals the multiplicative
    order of 10 modulo d (when gcd(10, d) = 1).

    Args:
        a: The base number (for decimal fractions, this is 10)
        modulus: The modulus to calculate against (the denominator d)

    Returns:
        The multiplicative order if it exists within modulus iterations, None otherwise
    """
    r = 1
    for k in range(1, modulus):
        r = (r * a) % modulus
        if r == 1:
            return k
    else:
        return None


def solution(*, max_val: int) -> int:
    """
    Find the value of d < max_val with the longest recurring decimal cycle in 1/d.

    This function uses number theory to determine the length of recurring cycles in
    decimal fractions. For a fraction 1/d, the length of its recurring decimal cycle
    equals the multiplicative order of 10 modulo d, when gcd(10, d) = 1.

    The function searches in descending order from max_val, which is efficient because:
    1. Larger primes tend to have longer cycles
    2. We only need to check values where gcd(d, 10) = 1 (i.e., d is not divisible by 2 or 5)

    Args:
        max_val: The upper bound for d (exclusive)

    Returns:
        The value of d < max_val for which 1/d has the longest recurring decimal cycle
    """
    return max((multiplicative_order(a=10, modulus=d), d)for i in range(100) for d in (max_val - i,)
               if d > 6 and gcd(d, 10) == 1)[1]


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 26: Reciprocal cycles
https://projecteuler.net/problem=26

Problem Description:
A unit fraction contains 1 in the numerator.
The decimal representation of the unit fractions with denominators 2 to 10 are given:

1/2 -> 0.5
1/3 -> 0.(3)
1/4 -> 0.25
1/5 -> 0.2
1/6 -> 0.1(6)
1/7 -> 0.(142857)
1/8 -> 0.125
1/9 -> 0.(1)
1/10 -> 0.1

Where 0.1(6) means 0.166666..., and has a 1-digit recurring cycle.
It can be seen that 1/7 has a 6-digit recurring cycle.

Problem Statement:
Find the value of d < 1000 for which 1/d contains the longest recurring cycle in its decimal fraction part.

Solution Overview:
This solution applies number theory to efficiently find the answer. For a unit fraction 1/d:

1. When d is divisible by 2 or 5, the decimal expansion will terminate or have a finite
   number of repeating digits followed by termination.

2. For other values of d (where gcd(d, 10) = 1), the length of the recurring cycle equals
   the multiplicative order of 10 modulo d - the smallest positive integer k such that
   10^k ≡ 1 (mod d).

3. The solution searches for values of d in descending order from the maximum value,
   as larger primes tend to have longer cycles, and returns the value with the longest cycle.

For values below 1000, the answer is 983, which has a recurring cycle of length 982.

''').strip()

if __name__ == '__main__':
    # When this module is run directly (not imported), evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments for controlling execution parameters
    args = parser.parse_args()

    # Set the logging level based on command-line arguments (e.g., debug, info, warning)
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    # - timeout: maximum time allowed for solution execution
    # - max_workers: controls parallel execution of test cases
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers for multiple test cases:
    # 1. max_val=10: Expected answer is 7 (1/7 has a 6-digit recurring cycle)
    # 2. max_val=100: Expected answer is 97 (1/97 has a 96-digit recurring cycle)
    # 3. max_val=1000: Expected answer is 983 (1/983 has a 982-digit recurring cycle)
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
