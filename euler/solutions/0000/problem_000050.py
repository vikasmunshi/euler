#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 50: Consecutive prime sum

Problem Statement:
The prime 41, can be written as the sum of six consecutive primes:
41 = 2 + 3 + 5 + 7 + 11 + 13.

This is the longest sum of consecutive primes that adds to a prime below one-hundred.

The longest sum of consecutive primes below one-thousand that adds to a prime, 
contains 21 terms, and is equal to 953.

Which prime, below one-million, can be written as the sum of the most consecutive primes?

Solution Approach:
This solution efficiently finds the prime that can be expressed as the sum of the most 
consecutive primes by using the following optimizations:

1. Generate all primes up to the maximum limit using a Sundaram sieve algorithm
2. Create a cumulative sum array (prefix sum) of primes for O(1) range sum calculations
3. Use a nested loop approach to check all possible ranges of consecutive primes:
   - Outer loop: iterate through possible end positions
   - Inner loop: iterate through possible start positions
4. For each range, calculate the sum using the prefix array and check if it's prime
5. Track the prime with the longest consecutive sequence

The algorithm prioritizes longer sequences and efficiently prunes impossible ranges.

Test Cases:
- For max_limit=100: 41 (sum of 6 consecutive primes: 2+3+5+7+11+13)
- For max_limit=1,000: 953 (sum of 21 consecutive primes)
- For max_limit=1,000,000: 997651 (the answer)

URL: https://projecteuler.net/problem=50
Answer: 997651
"""
from itertools import accumulate
from typing import Tuple, List, Set

from euler.primes import gen_primes_sundaram_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

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

    This function identifies the prime number below the given limit that can be expressed
    as the sum of the longest possible sequence of consecutive prime numbers. It uses
    prefix sums for efficient calculation of consecutive prime sequences.

    Args:
        max_limit: The upper bound for the prime to be found

    Returns:
        The prime number that can be written as the sum of the most consecutive primes

    Examples:
        >>> solution(max_limit=100)
        41  # Sum of 6 consecutive primes: 2+3+5+7+11+13
        >>> solution(max_limit=1000)
        953  # Sum of 21 consecutive primes
        >>> solution(max_limit=1000000)
        997651  # The answer to the main problem
    """
    primes_tuple: Tuple[int, ...] = gen_primes_sundaram_sieve(max_limit=max_limit)
    prime_sums: List[int] = [0] + list(accumulate(primes_tuple))
    primes: Set[int] = set(primes_tuple)  # Convert to set for O(1) lookups

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


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast
    from euler.evaluator import module_main

    # The `module_main` function handles the evaluation process by:
    # 1. Extracting the problem number from the file name for contextual usage.
    # 2. Accepting command-line arguments to configure execution, e.g., timeout or threading options.
    # 3. Running the `solution` function for all test cases defined in `problem_args_list`.
    # 4. Outputting the test results, including details such as whether the test passed/failed and time taken.
    # 5. Returning an appropriate exit code (exit code 0 indicates success, non-zero for failures).

    # The `SystemExit` ensures the program exits with the exit code returned by `module_main`.
    raise SystemExit(module_main(module_name=__file__,
                                 solution=cast(SolutionProtocol, solution),
                                 args_list=problem_args_list))
