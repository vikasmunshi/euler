#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 49
# https://projecteuler.net/problem=49
# Answer: 2969 6299 9629
# Notes: 
"""
Project Euler Problem 49: Prime permutations

The arithmetic sequence 1487, 4817, 8147, in which each term increases by 3330, 
is unusual in two ways:
(i) each of the three terms are prime, and
(ii) each of the 4-digit numbers are permutations of one another.

There are no arithmetic sequences made up of three 1-, 2-, or 3-digit primes, 
exhibiting this property, but there is one other 4-digit increasing sequence.

What 12-digit number do you form by concatenating the three terms in this sequence?

Solution approach:
-----------------
This module identifies arithmetic sequences of n-digit prime numbers where all numbers
are permutations of each other. The implementation follows these steps:

1. Generate all n-digit prime numbers using the Sundaram sieve algorithm
2. For each prime, identify all its digit permutations that are also prime
3. For each set of permuted primes with at least 3 members, find all pairwise differences
4. Identify arithmetic sequences by finding groups of exactly 3 numbers with the same
   absolute difference between consecutive terms
5. Return these sequences as space-separated strings in ascending numerical order

Key optimizations:
- Efficient prime generation using the Sundaram sieve algorithm
- String-based permutation generation to simplify digit manipulation
- Using defaultdict to efficiently track differences between prime pairs
- Set data structures to eliminate duplicates automatically

For n=4 (4-digit primes), the solution finds two sequences:
- 1487 4817 8147 (the example given in the problem)
- 2969 6299 9629 (the answer to the problem)

For n=5 (5-digit primes), the solution finds 42 different sequences with this property,
showing how this mathematical pattern extends to larger numbers.

Performance characteristics:
- Time complexity: O(P * n!) where P is the number of n-digit primes and n is the number of digits
- Space complexity: O(P) where P is the number of n-digit primes
"""
import textwrap
from collections import defaultdict
from itertools import permutations, combinations
from typing import Set

from euler.primes import gen_primes_sundaram_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 4}, answer={'1487 4817 8147', '2969 6299 9629'}, ),
    ProblemArgs(kwargs={'n': 5},
                answer={'11483 14813 18143', '11497 41719 71941', '12713 13217 13721', '12739 17239 21739',
                        '12757 17257 21757', '12799 17299 21799', '14821 48121 81421', '14831 31481 48131',
                        '18503 51803 85103', '19543 35491 51439', '20161 20611 21061', '20353 25303 30253',
                        '20359 25309 30259', '20747 24077 27407', '23887 28387 32887', '25087 52807 80527',
                        '25793 59273 92753', '25981 59281 92581', '29669 62969 96269', '31489 34819 38149',
                        '31489 39841 48193', '32969 63299 93629', '34961 39461 43961', '35407 40357 45307',
                        '35671 53617 71563', '37561 51637 65713', '49547 54497 59447', '55603 56053 56503',
                        '60373 63703 67033', '60757 65707 70657', '61487 64817 68147', '62597 65927 69257',
                        '62773 67723 72673', '63499 63949 64399', '67829 68279 68729', '68713 78163 87613',
                        '71947 74719 77491', '73589 78593 83597', '76717 77167 77617', '76819 81769 86719',
                        '89387 93887 98387', '92381 92831 93281'}, ),
]


def solution(*, n: int) -> Set[str]:
    """Find arithmetic sequences of prime numbers that are permutations of each other.

    This function identifies sets of exactly three n-digit prime numbers that form an arithmetic
    sequence (with equal differences between consecutive terms) and are permutations of
    each other's digits.

    Args:
        n: int - The number of digits in the prime numbers to consider
              For n=4, finds 4-digit prime sequences
              For n=5, finds 5-digit prime sequences

    Returns:
        Set[str] - A set of strings, each containing three space-separated prime numbers
                   that form an arithmetic sequence and are permutations of each other.
                   The numbers in each string are sorted in ascending order.

    Example:
        >>> solution(n=4)
        {'1487 4817 8147', '2969 6299 9629'}
    """
    sequences: Set[str] = set()
    min_n_digit_hum = 10 ** (n - 1)
    n_digit_primes: Set[str] = {str(p) for p in gen_primes_sundaram_sieve(max_limit=10 ** n) if p > min_n_digit_hum}
    for prime in n_digit_primes:
        permuted_primes = set(p for d in permutations(prime) if (p := ''.join(d)) in n_digit_primes)
        if len(permuted_primes) >= 3:
            differences = defaultdict(set)
            for prime_i, prime_j in combinations(permuted_primes, 2):
                differences[abs(int(prime_j) - int(prime_i))].update((prime_i, prime_j))
            for difference, primes in differences.items():
                if len(primes) == 3:
                    sequences.add(' '.join(sorted(primes)))
    return sequences


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 49
https://projecteuler.net/problem=49
The arithmetic sequence, 1487, 4817, 8147, in which each of the terms increases by 3330, is unusual in two ways:
(i) each of the three terms are prime, and,
(ii) each of the 4-digit numbers are permutations of one another.
There are no arithmetic sequences made up of three 1-, 2-, or 3-digit primes, exhibiting this property,
but there is one other 4-digit increasing sequence.
What 12-digit number do you form by concatenating the three terms in this sequence?

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
