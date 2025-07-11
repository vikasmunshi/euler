#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 37: Truncatable primes

Problem Statement:
The number 3797 has an interesting property. Being prime itself, it is possible to continuously remove digits from left to right, and remain prime at each stage: 3797, 797, 97, and 7. Similarly we can work from right to left: 3797, 379, 37, and 3.
Find the sum of the only eleven primes that are both truncatable from left to right and right to left.
NOTE: 2, 3, 5, and 7 are not considered to be truncatable primes.

Solution Approach:
This solution uses an efficient prime sieve to generate prime numbers one at a time, then tests
each prime for the truncatable property. A prime is truncatable if all numbers formed by
removing digits from either left or right remain prime. The algorithm stores primes in a set
for O(1) lookups when checking truncations, and terminates once all 11 truncatable primes are found.

Key optimizations:
1. Using a memory-efficient sieve that generates primes indefinitely without storing a large array
2. Skipping single-digit primes (2, 3, 5, 7) as specified in the problem
3. Checking both left and right truncations simultaneously
4. Early termination once 11 truncatable primes are found (as stated in the problem)

Examples of truncatable primes:
- 3797: Left truncations (3797, 797, 97, 7) and right truncations (3797, 379, 37, 3) are all prime
- 23: Left truncation (23, 3) and right truncation (23, 2) are all prime

URL: https://projecteuler.net/problem=37
Answer: 748317
"""
from typing import Set, List

from euler.primes import gen_primes_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=748317, ),  # The sum of all 11 truncatable primes
]


def sum_truncatable_primes() -> int:
    """
    Find the sum of all truncatable primes, which remain prime when digits are removed.

    A truncatable prime is a prime number that remains prime after any digit is
    removed from left to right or right to left. For example, 3797 is truncatable
    because all of 3797, 797, 97, 7 (left truncation) and 3797, 379, 37, 3 (right
    truncation) are prime. The problem states there are exactly 11 such primes.

    Returns:
        The sum of all 11 truncatable primes

    Example:
        >>> sum_truncatable_primes()
        748317
    """
    primes: Set[str] = set()  # Set of all primes encountered so far (as strings)
    truncatable_primes: List[int] = list()  # List to collect truncatable primes

    # Generate primes and check for truncatable property
    for prime_num in gen_primes_sieve():
        prime = str(prime_num)
        primes.add(prime)  # Add current prime to our set

        # Skip single-digit primes (as specified in the problem)
        if int(prime) < 10:
            continue

        # Check if all truncations are prime
        # Generate all left and right truncations and verify they're all prime
        # Left truncation: prime[i:] (e.g., 3797 → 797 → 97 → 7)
        # Right truncation: prime[:i] (e.g., 3797 → 379 → 37 → 3)
        if not any(pl not in primes or pr not in primes
                   for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))]):
            truncatable_primes.append(prime_num)

        # We only need to find 11 truncatable primes (as stated in the problem)
        if len(truncatable_primes) == 11:
            break

    # Return the sum of all truncatable primes
    return sum(truncatable_primes)

# Create an alias for the sum_truncatable_primes function to match the expected solution interface
# This allows the function to be named descriptively while still conforming to the
# Project Euler framework's convention of using 'solution' as the entry point
solution = sum_truncatable_primes

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
