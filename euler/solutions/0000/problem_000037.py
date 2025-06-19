#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 37: Truncatable Primes
# https://projecteuler.net/problem=37
# Answer: 748317
#
# PROBLEM DESCRIPTION:
# The number 3797 has an interesting property. Being prime itself, it is possible to
# continuously remove digits from left to right, and remain prime at each stage: 3797, 797, 97, and 7.
# Similarly, we can work from right to left: 3797, 379, 37, and 3.
# Find the sum of the only eleven primes that are both truncatable from left to right and right to left.
# NOTE: 2, 3, 5, and 7 are not considered to be truncatable primes.
#
# SOLUTION APPROACH:
# 1. Generate prime numbers using an efficient sieve implementation
# 2. For each prime (greater than single digit), check if all its truncations are also prime
# 3. Collect the first 11 primes that satisfy this condition
# 4. Return their sum
#
# KEY INSIGHTS:
# - There are exactly 11 such primes, as stated in the problem
# - Single-digit primes are excluded by definition (as they cannot be truncated further)
# - We need to check both left-to-right and right-to-left truncations
# - The solution can terminate early once we find all 11 truncatable primes
#
# OPTIMIZATIONS:
# - Using a sieve algorithm for efficient prime generation
# - Storing primes in a set for O(1) lookup when checking truncations
# - Generating primes lazily to avoid unnecessary computation
# - Early termination once all 11 truncatable primes are found
#
# MATHEMATICAL NOTES:
# - A truncatable prime must not contain the digit 0 (as this would make a truncation non-prime)
# - The largest truncatable prime is 739397 (verified experimentally)
# - All truncatable primes must start and end with a prime digit (2, 3, 5, or 7)
# - The 11 truncatable primes are: 23, 37, 53, 73, 313, 317, 373, 797, 3137, 3797, and 739397
#
# TIME COMPLEXITY: O(P log P), where P is the value of the largest truncatable prime
# SPACE COMPLEXITY: O(P), for storing the set of primes up to the largest truncatable prime
import textwrap
from typing import Generator, cast, Dict, List

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test case for the truncatable primes problem
#
# There is only one test case for this problem since:  
# 1. The problem has a unique answer (sum of exactly 11 truncatable primes)
# 2. No parameters are needed to customize the solution
# 
# The expected answer is 748,317, which is the sum of the 11 truncatable primes:
# 23 + 37 + 53 + 73 + 313 + 317 + 373 + 797 + 3137 + 3797 + 739397 = 748,317
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},  # No parameters needed for this problem
        answer=748317,  # Sum of the 11 truncatable primes
    ),
]


def gen_primes_sieve() -> Generator[str, None, None]:
    """Generate prime numbers efficiently using a modified sieve algorithm.

    This function implements a memory-efficient version of the Sieve of Eratosthenes
    that generates prime numbers one at a time without storing a large boolean array.
    It uses a dictionary to track composites and their prime factors.

    The implementation follows these steps:
    1. Use a dictionary to track composite numbers and their prime factors
    2. For each number, check if it is in known_composites dictionary
    3. If not, it's prime - yield it and mark its square as composite
    4. If it is composite, update future composites with its factors and remove it

    Returns primes as strings to facilitate truncation operations in the main algorithm.

    Yields:
        Prime numbers as strings, starting from 2 and continuing indefinitely

    Notes:
        - This is a memory-efficient implementation of the sieve algorithm
        - Using a dictionary instead of an array allows us to sieve indefinitely
        - The algorithm only tracks composite numbers that are currently needed
        - Prime numbers are returned as strings for easier manipulation in the main algorithm
    """
    known_composites: Dict[int: List[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:
            # The current number is prime - yield it and mark its square as composite
            yield str(current_number)
            known_composites[current_number * current_number] = [current_number]
        else:
            # Current number is composite - update future composites
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            # Remove the current composite from the dictionary to save memory
            del known_composites[current_number]
        current_number += 1


def sum_truncatable_primes() -> int:
    """Find the sum of all truncatable primes.

    A truncatable prime is a prime number that remains prime when digits are
    removed one by one from the left or from the right. For example, 3797 is truncatable
    because all of these numbers are prime:
    - Left truncations: 3797, 797, 97, 7
    - Right truncations: 3797, 379, 37, 3

    According to the problem statement, there are exactly 11 such primes (excluding
    single-digit primes), and this function finds them all and returns their sum.

    Implementation Details:
    1. Use a sieve to generate primes efficiently
    2. Store the generated primes in a set for O(1) lookup
    3. For each prime > 9, check all its truncations (both left and right)
    4. If all truncations are prime, add it to the list of truncatable primes
    5. Stop once we've found all 11 truncatable primes
    6. Return the sum of these primes

    Returns:
        The sum of all 11 truncatable primes

    Notes:
        - The definition does not consider Single-digit primes (2, 3, 5, 7) truncatable
        - The algorithm uses a list comprehension to generate all possible truncations
        - The algorithm terminates after finding 11 primes as specified in the problem
        - The answer is 748,317, which is the sum of the 11 truncatable primes
        - The 11 truncatable primes are: 23, 37, 53, 73, 313, 317, 373, 797, 3137, 3797, and 739,397
    """
    primes = set()  # Set of all primes encountered so far (as strings)
    truncatable_primes = list()  # List to collect truncatable primes

    # Generate primes and check for truncatable property
    for prime in gen_primes_sieve():
        primes.add(prime)  # Add current prime to our set

        # Skip single-digit primes (as specified in the problem)
        if int(prime) < 10:
            continue

        # Check if all truncations are prime
        # For each position i, generate both left and right truncations
        # pl = prime with i digits removed from the left
        # pr = prime with i digits removed from the right
        if not any(pl not in primes or pr not in primes
                   for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))]):
            truncatable_primes.append(prime)

        # We only need to find 11 truncatable primes (as stated in the problem)
        if len(truncatable_primes) == 11:
            break

    # Return the sum of all truncatable primes
    return sum(int(p) for p in truncatable_primes)


solution = cast(SolutionProtocol, sum_truncatable_primes)

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 37: Truncatable Primes
https://projecteuler.net/problem=37

Problem Description:
The number 3797 has an interesting property. Being prime itself, it is possible to
continuously remove digits from left to right, and remain prime at each stage: 3797, 797, 97, and 7.
Similarly we can work from right to left: 3797, 379, 37, and 3.

Find the sum of the only eleven primes that are both truncatable from left to right and right to left.
NOTE: 2, 3, 5, and 7 are not considered to be truncatable primes.

Solution Approach:
1. Generate prime numbers efficiently using a modified sieve algorithm
2. For each prime number greater than 9:
   a. Check if all its left truncations are prime (e.g., for 3797: 797, 97, 7)
   b. Check if all its right truncations are prime (e.g., for 3797: 379, 37, 3)
   c. If both conditions are met, it's a truncatable prime
3. Collect the first 11 truncatable primes and return their sum

Algorithm Details:
- The sieve implementation uses a dictionary to track composites and their factors
- Primes are stored as strings to facilitate easy truncation operations
- All possible truncations are generated using slicing operations
- The algorithm terminates after finding 11 truncatable primes as stated in the problem

Performance Considerations:
- Using a set for O(1) prime lookups significantly improves performance
- The sieve algorithm is memory-efficient and suitable for generating primes indefinitely
- Early termination once all 11 truncatable primes are found saves computation

Mathematical Insights:
- Truncatable primes must not contain the digit 0 (as 0 at the start would not be a valid number)
- All digits in a truncatable prime must be carefully chosen so that all truncations remain prime
- The 11 truncatable primes (in ascending order) are:
  23, 37, 53, 73, 313, 317, 373, 797, 3137, 3797, and 739397
- The largest truncatable prime (739397) is significantly larger than the others

Construction Rules for Truncatable Primes:
1. Must begin and end with a prime digit (2, 3, 5, or 7)
2. Cannot contain the digit 0 (would make a truncation non-prime)
3. Cannot contain the digit 4, 6, 8, or 9 at the start (would make a truncation non-prime)
4. The construction is highly constrained, explaining why only 11 such primes exist

Time Complexity: O(P log P), where P is the largest truncatable prime (739397)
Space Complexity: O(P) for storing the set of primes

The 11 truncatable primes are: 23, 37, 53, 73, 313, 317, 373, 797, 3137, 3797, and 739,397
The sum of all truncatable primes is 748,317 (final answer)
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
