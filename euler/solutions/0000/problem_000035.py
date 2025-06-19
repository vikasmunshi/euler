#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Solution to Project Euler problem 35: Circular Primes
# https://projecteuler.net/problem=35
# Answer: answers={10: 4, 100: 13, 10 ** 6: 55, 10 ** 8: 55}
# Notes: 
# This solution finds all circular primes below a given limit using the Sundaram sieve algorithm.
# 
# A circular prime is a prime number that remains prime after any cyclic rotation of its digits.
# For example, 197 is a circular prime because all rotations (197, 971, 719) are prime.
#
# Key Optimizations and Features:
# 1. Uses the Sundaram sieve for efficient prime generation
# 2. Employs set operations for O(1) membership testing
# 3. Early filtering: Rejects candidates with even digits or the digit 5
# 4. Special case handling for single-digit primes
#
# Mathematical Properties:
# * Multi-digit circular primes can only contain digits 1, 3, 7, and 9
# * There are exactly 55 circular primes below 10^8
# * This count doesn't increase between 10^6 and 10^8, showing the
#   extreme rarity of circular primes in higher ranges
#
# Performance characteristics: O(N log log N) time complexity, where N is the upper limit
import textwrap
from typing import cast, Set

from euler.primes import gen_primes_sundaram_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Test cases for validating the circular primes solution across different magnitude limits
#
# The test cases demonstrate the following progression of circular primes:
# - At limit 10: The 4 single-digit primes (2, 3, 5, 7) are all circular by definition
# - At limit 100: 13 circular primes total, including new multi-digit primes like 11, 13, 17, etc.
# - At limit 1,000: 25 circular primes, showing continued but slowing growth
# - At limit 10^6: 55 circular primes, the target count requested in the original problem
# - At limit 10^8: Still only 55 circular primes, demonstrating that no additional circular primes
#   exist between 10^6 and 10^8. This is a mathematically interesting property showing the
#   extreme rarity of circular primes in higher number ranges.
#
# This pattern illustrates why the algorithm scales well - for very large inputs, we're still
# working with a small, bounded set of actual circular primes.
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_limit': 10},  # There are 4 circular primes below 10: 2, 3, 5, 7
        answer=4,
    ),
    ProblemArgs(
        kwargs={'max_limit': 100},  # 13 circular primes below 100, as listed in the problem description
        answer=13,
    ),
    ProblemArgs(
        kwargs={'max_limit': 1000},  # 25 circular primes below 1000
        answer=25,
    ),
    ProblemArgs(
        kwargs={'max_limit': 10 ** 6},  # The main problem: 55 circular primes below one million
        answer=55,
    ),
    ProblemArgs(
        kwargs={'max_limit': 10 ** 8},  # Note: No new circular primes found between 10^6 and 10^8
        answer=55,
    ),
]


def get_rotated_numbers(*, num: int) -> Set[int]:
    """Generate all possible rotations of the digits of a number.

    This function takes an integer and returns all possible rotations of its digits
    as a set for efficient lookups. A rotation is created by moving digits from the
    beginning to the end of the number.

    For example, for the number 197, it returns the set {197, 971, 719}.
    For single-digit numbers, it returns a set containing only the number itself.

    Args:
        num: The input integer to generate rotations for

    Returns:
        Set of all possible digit rotations of the input number
    """
    str_num: str = str(num)
    # For single-digit numbers, return the set with only the number itself, else return the set of all rotations
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


def solution(*, max_limit: int) -> int:
    """Find the number of circular primes below a given limit.

    A circular prime is a prime number that remains prime after any cyclic rotation
    of its digits. This function calculates how many such primes exist below the
    specified limit.

    Implementation Details:
    1. Generate all primes below max_limit using the Sundaram sieve
    2. Convert the list to a set for O(1) lookups
    3. For each prime, check if all its digit rotations are also prime i.e., in the set of primes
    4. Return the count of such circular primes

    Examples:
    - Below 10: {2, 3, 5, 7} (4 circular primes)
    - Below 100: {2, 3, 5, 7, 11, 13, 17, 31, 37, 71, 73, 79, 97} (13 circular primes)
    - Below 1,000,000: 55 circular primes

    Args:
        max_limit: The upper limit for the search (exclusive)

    Returns:
        The count of circular primes below the given limit
    """
    primes = set(gen_primes_sundaram_sieve(max_limit=max_limit))
    circular_primes = [
        prime for prime in primes
        if prime < 10
           or (not any(d in str(prime) for d in '024568')
               and not any(rotated_number not in primes for rotated_number in get_rotated_numbers(num=prime)))
    ]
    return len(circular_primes)


solution = cast(SolutionProtocol, solution)

solution.__doc__ = textwrap.dedent(r'''
Solution to Project Euler problem 35: Circular Primes
https://projecteuler.net/problem=35

Problem Description:
The number, 197, is called a circular prime because all rotations of the digits: 197, 971, and 719, are themselves prime.
There are thirteen such primes below 100: 2, 3, 5, 7, 11, 13, 17, 31, 37, 71, 73, 79, and 97.
How many circular primes are there below one million?

Solution Approach:
1. Generate all prime numbers below the given limit using the Sundaram sieve algorithm
2. For each prime, generate all its digit rotations
3. Check if all rotations are also prime
4. Count the number of such circular primes

Algorithm Details:
- We use the Sundaram sieve for efficient prime generation
- For each prime, we create a set of all its digit rotations
- A prime is circular if all its rotations are also in our set of primes
- We implement this check efficiently using set operations
- Early filtering: Any prime with even digits (0,2,4,6,8) cannot be circular (except 2)
  because at least one rotation would be divisible by 2

Performance Considerations:
- Using sets for both primes and rotations enables O(1) lookups
- Single-digit primes are handled as a special case
- The Sundaram sieve is more memory-efficient than the Eratosthenes sieve for large limits
- The algorithm scales well to handle limits up to 10^8

Time Complexity: O(N log log N), where N is the max_limit
Space Complexity: O(π(N)), where π(N) is the prime-counting function (number of primes less than N)

Mathematical Insight on Circular Primes:
The extreme rarity of circular primes can be explained mathematically:

1. For a number to be a circular prime, all of its rotations must be prime
2. Any multi-digit circular prime cannot contain the digits 0, 2, 4, 6, or 8
   (except for 2 itself), because any rotation placing these digits at the end
   would create an even number, which cannot be prime
3. Similarly, numbers containing digit 5 (except 5 itself) cannot be circular primes
   because any rotation placing 5 at the end would be divisible by 5
4. This means circular primes with more than one digit can only contain the digits 1, 3, 7, and 9
5. As numbers get larger, the probability that all rotations remain prime decreases exponentially
6. This explains why there are only 55 circular primes below 10^8, and why there are likely
   very few (if any) undiscovered circular primes larger than this

The complete list of the 55 circular primes up to 10^8 is:
[2, 3, 5, 7, 11, 13, 17, 31, 37, 71, 73, 79, 97, 113, 131, 197, 199, 311, 337, 373, 719, 733, 919, 971, 991, 1193, 1931,
3119, 3779, 7793, 7937, 9311, 9377, 11939, 19391, 19937, 37199, 39119, 71993, 91193, 93719, 93911, 99371, 193939, 199933,
319993, 331999, 391939, 393919, 919393, 933199, 939193, 939391, 993319, 999331]
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
