#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 49: Prime permutations

Problem Statement:
The arithmetic sequence, 1487, 4817, 8147, in which each of the terms increases by 3330, 
is unusual in two ways: (i) each of the three terms are prime, and, (ii) each of the 
4-digit numbers are permutations of one another.

There are no arithmetic sequences made up of three 1-, 2-, or 3-digit primes, exhibiting 
this property, but there is one other 4-digit increasing sequence.

What 12-digit number do you form by concatenating the three terms in this sequence?

Solution Approach:
This solution searches for prime number arithmetic sequences with special properties:

1. Generate all n-digit prime numbers using the Sundaram sieve algorithm
2. For each prime, find all its digit permutations that are also prime
3. For primes sharing the same set of digits, identify those that form arithmetic 
   sequences (have equal differences between consecutive terms)
4. Return all such sequences of exactly three primes

The algorithm uses defaultdict to efficiently group prime pairs by their differences,
and then identifies complete sequences by finding difference groups with exactly three
prime numbers.

Test Cases:
- For 4-digit primes: Two sequences are found: 
  * 1487, 4817, 8147 (explicitly mentioned in the problem)
  * 2969, 6299, 9629 (the answer to the problem)
- For 5-digit primes: 42 different sequences are found (additional test)

URL: https://projecteuler.net/problem=49
Answer: 296962999629
"""
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
    """
    Find arithmetic sequences of prime numbers that are permutations of each other.

    This solution searches for sets of exactly three n-digit prime numbers that form an 
    arithmetic sequence and are permutations of each other's digits. For the original 
    problem where n=4, this includes the known sequence 1487, 4817, 8147 and the sequence 
    we need to identify, 2969, 6299, 9629.

    Args:
        n: The number of digits in the prime numbers to consider

    Returns:
        A set of strings, each containing three space-separated prime numbers in ascending order

    Examples:
        >>> solution(n=4)
        {'1487 4817 8147', '2969 6299 9629'}
        >>> len(solution(n=5))  # Number of 5-digit sequences
        42
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
