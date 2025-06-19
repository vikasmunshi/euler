#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 50
# https://projecteuler.net/problem=50
# Answer: 997651
# Notes: 
"""
Solution to Project Euler Problem 50: Consecutive Prime Sum

This module implements a solution to find the prime below a given limit that can be written
as the sum of the most consecutive primes.

Problem Description:
    The prime 41 can be written as the sum of six consecutive primes: 2 + 3 + 5 + 7 + 11 + 13.
    This is the longest sum of consecutive primes that adds to a prime below one-hundred.
    The longest sum of consecutive primes below one-thousand that adds to a prime, contains
    21 terms, and is equal to 953.
    The task is to find which prime, below a given limit, can be written as the sum of the
    most consecutive primes.

Algorithm:
    1. Generate all primes up to the maximum limit using the Sundaram sieve method
    2. Create a list of cumulative sums of these primes to efficiently calculate ranges
    3. For each possible starting position, check consecutive sums to find prime sums
    4. Keep track of the prime that is the sum of the longest consecutive sequence

The solution handles multiple test cases with different maximum limits.

Time Complexity: O(n²) where n is the number of primes below max_limit
Space Complexity: O(n) for storing the primes and cumulative sums
"""
import textwrap
from itertools import accumulate

from euler.primes import gen_primes_sundaram_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# List of test cases with their expected answers
# Each test case specifies a maximum limit and the corresponding prime answer
# These test cases verify the solution for different input sizes:
# - 10^2: Longest consecutive prime sum below 100
# - 10^3: Longest consecutive prime sum below 1,000
# - etc. up to 10^7
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_limit': 10 ** 2}, answer=41, ),
    ProblemArgs(kwargs={'max_limit': 10 ** 3}, answer=953, ),
    ProblemArgs(kwargs={'max_limit': 10 ** 4}, answer=9521, ),
    ProblemArgs(kwargs={'max_limit': 10 ** 5}, answer=92951, ),
    ProblemArgs(kwargs={'max_limit': 10 ** 6}, answer=997651, ),
    ProblemArgs(kwargs={'max_limit': 10 ** 7}, answer=9951191, ),
]


def solution(*, max_limit: int) -> int:
    """
    Find the prime below max_limit that can be written as the sum of the most consecutive primes.

    This function finds the prime number below the given maximum limit that can be expressed
    as the sum of the longest sequence of consecutive prime numbers.

    Args:
        max_limit (int): The upper bound for the prime to be found

    Returns:
        int: The prime number below max_limit that can be written as the sum of the most
             consecutive primes

    Algorithm:
        1. Generate all primes up to max_limit using the Sundaram sieve algorithm
        2. Create a cumulative sum array of primes for efficient range sum computation
        3. For each possible range (i,j), check if the sum is a prime number
        4. Track the prime with the longest consecutive sequence

    Example:
        For max_limit=100, returns 41 (sum of 6 consecutive primes: 2+3+5+7+11+13)
        For max_limit=1000, returns 953 (sum of 21 consecutive primes)
    """
    primes = gen_primes_sundaram_sieve(max_limit=max_limit)
    prime_sums = [0] + list(accumulate(primes))
    primes = set(primes)  # Convert to set for O(1) lookups

    # Initialize variables to track the longest sequence and its corresponding prime
    number_of_primes_in_sum, prime = 0, 0

    # Outer loop: for each possible end position in the cumulative sum array
    for i in range(number_of_primes_in_sum, len(prime_sums), 1):
        # Inner loop: for each possible start position, starting from positions that could
        # potentially form longer sequences than what we've already found
        for j in range(i - number_of_primes_in_sum - 1, -1, -1):
            # Calculate the sum of consecutive primes from position j to i
            possible_prime = prime_sums[i] - prime_sums[j]

            # Skip if the sum exceeds our limit
            if possible_prime > max_limit:
                break

            # If the sum is itself a prime number and the sequence is longer than previous ones
            if possible_prime in primes:
                number_of_primes_in_sum = i - j  # Update sequence length
                prime = possible_prime  # Update the prime answer

    return prime


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 50
https://projecteuler.net/problem=50
The prime 41, can be written as the sum of six consecutive primes:
41 = 2 + 3 + 5 + 7 + 11 + 13.
This is the longest sum of consecutive primes that adds to a prime below one-hundred.
The longest sum of consecutive primes below one-thousand that adds to a prime, contains 21 terms, and is equal to 953.
Which prime, below one-million, can be written as the sum of the most consecutive primes?

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
