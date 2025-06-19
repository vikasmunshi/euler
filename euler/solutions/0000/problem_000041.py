#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 41
# https://projecteuler.net/problem=41
# Answer: 7652413
# Notes: 
"""
Solution to Project Euler problem 41 - Pandigital prime.

This module finds the largest n-digit pandigital prime number.
A pandigital number uses all digits from 1 to n exactly once.

The solution uses mathematical insights to optimize the search:
- 9-digit pandigitals: sum = 45, divisible by 3, thus not prime
- 8-digit pandigitals: sum = 36, divisible by 3, thus not prime
- 6-digit pandigitals: sum = 21, divisible by 3, thus not prime
- 5-digit pandigitals: sum = 15, divisible by 3, thus not prime
- 3-digit pandigitals: sum = 6, divisible by 3, thus not prime
- 2-digit pandigitals: sum = 3, divisible by 3, thus not prime
- 1-digit pandigitals: only 1, which is not prime by definition

Thus, we only need to check 7-digit and 4-digit pandigitals.

Functions:
    is_prime: Tests if a number is prime
    largest_pandigital_prime: Finds the largest pandigital prime
"""
import textwrap
from itertools import permutations
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},
        answer=7652413,
    ),
]


def is_prime(n: int) -> bool:
    """
    Check if a number is prime.

    A prime number is a natural number greater than 1 that is not divisible
    by any positive integer other than 1 and itself.

    Parameters:
        n: The integer to check for primality

    Returns:
        True if the number is prime, False otherwise

    Notes:
        - This implementation uses trial division up to the square root of n
        - It does not handle special cases like n <= 1
        - Time complexity: O(√n)
    """
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def largest_pandigital_prime() -> int:
    """
    Find the largest n-digit pandigital prime number.

    A pandigital number is one that uses all digits from 1 to n exactly once.
    For example, 2143 is a 4-digit pandigital number.

    Returns:
        The largest pandigital prime number

    Algorithm:
    1. Using number theory, we know that:
       - A number is divisible by 3 if the sum of its digits is divisible by 3
       - The sum of digits 1 through 9 is 45 (divisible by 3)
       - The sum of digits 1 through 8 is 36 (divisible by 3)
       - Similarly, 6, 5, 3, and 2-digit pandigitals are all divisible by 3
    2. Therefore, we only need to check 7-digit and 4-digit pandigitals
    3. Start with 7-digit pandigitals (larger) and check primality
    4. If none is found, check 4-digit pandigitals
    5. Return the first (largest) prime found

    Optimization:
    - We reverse the digits before generating permutations to get the
      largest pandigitals first, ensuring we find the answer quickly
    """
    pandigital_primes = (
        number
        for length in (7, 4)  # all other length pandigital numbers are divisible by 3
        for number in (int(''.join(digits)) for digits in permutations(reversed('123456789'[:length]), length))
        if is_prime(number)
    )
    return next(pandigital_primes)


solution = cast(SolutionProtocol, largest_pandigital_prime)

# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 41
https://projecteuler.net/problem=41
We shall say that an n-digit number is pandigital if it makes use of all the digits 1 to n exactly once.
For example, 2143 is a 4-digit pandigital and is also prime.
What is the largest n-digit pandigital prime that exists?

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
