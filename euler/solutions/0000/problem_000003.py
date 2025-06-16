#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Solution to Project Euler problem 3: Largest Prime Factor

https://projecteuler.net/problem=3

Problem statement:
    The prime factors of 13,195 are 5, 7, 13 and 29.
    What is the largest prime factor of the number 600851475143?

Answer: 6857

Strategy:
    1. Start by checking if the number is divisible by 2 (the smallest prime)
    2. Continue with odd factors starting from 3
    3. For each prime factor, divide the number completely by that factor
    4. Optimize by only checking factors up to the square root of the current number
    5. If no factor is found and the number is greater than 1, it is prime

Complexity analysis:
    Time complexity: O(sqrt(n)) where n is the input number
    Space complexity: O(1) - only uses a constant amount of extra space
"""
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'number': 13195},
        answer=29,
    ),
    ProblemArgs(
        kwargs={'number': 600851475143},
        answer=6857,
    ),
]


def reduce(num: int, divisor: int) -> int:
    """Reduce a number by dividing it by a divisor until it's no longer divisible.

    Args:
        num: The number to reduce
        divisor: The divisor to use for reduction

    Returns:
        The reduced number after removing all instances of the divisor

    Example:
        >>> reduce(48, 2) # 48 / 2^4 = 3
        3
        >>> reduce(45, 3) # 45 / 3^2 = 5
        5
    """
    # First division to ensure the num is at least divisible once by divisor
    num //= divisor

    # Continue dividing as long as possible
    while num % divisor == 0:
        num //= divisor

    return num


def solution(*, number: int) -> int:
    """Find the largest prime factor of a given number.

    This function uses a trial division algorithm to find prime factors.
    It handles even numbers separately for optimization, then checks only odd
    numbers. The search space is limited to the square root of the current number.

    Args:
        number: The number to find the largest prime factor of

    Returns:
        The largest prime factor of the input number

    Example:
        >>> solution(number=13195)
        29
        >>> solution(number=600851475143)
        6857
    """
    # Handle the smallest prime factor (2) separately for optimization
    if number % 2 == 0:
        remaining_number = reduce(number, 2)
        largest_factor = 2
    else:
        remaining_number = number
        largest_factor = 1

    # Initialize the potential factor and the search limit
    current_factor = 3
    search_limit = int(remaining_number ** 0.5)

    # Check odd factors up to the square root of the current number
    while remaining_number > 1 and current_factor <= search_limit:
        if remaining_number % current_factor == 0:
            # When a factor is found, reduce the number and update the largest factor
            remaining_number = reduce(remaining_number, current_factor)
            largest_factor = current_factor
            # Update the search limit based on the new reduced number
            search_limit = int(remaining_number ** 0.5)
        current_factor += 2  # Check only odd numbers

    # If remaining_number > 1, it is the largest prime factor
    # Otherwise, return the largest factor found so far
    return remaining_number if remaining_number > 1 else largest_factor


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

# Create a well-formatted docstring for documentation and help
solution.__doc__ = textwrap.dedent('''
    Solution to Project Euler problem 3: Largest Prime Factor

    Problem Statement:
    -----------------
    The prime factors of 13195 are 5, 7, 13 and 29.
    What is the largest prime factor of the number 600851475143?

    This solution uses an optimized trial division algorithm that:
    1. Handles the even prime factor (2) separately
    2. Only checks odd factors from 3 upward
    3. Limits the search space to sqrt(n) where n is the current number
    4. Completely removes each prime factor before continuing

    Examples:
        >>> solution(number=13195)
        29
        >>> solution(number=600851475143)
        6857
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
