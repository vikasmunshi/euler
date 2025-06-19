#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 46
# https://projecteuler.net/problem=46
# Answer: 5777
# Notes: 
"""Solution to Project Euler problem 46: Goldbach's Other Conjecture.

This module finds the smallest odd composite number that cannot be written as the
sum of a prime and twice a square, disproving Goldbach's conjecture that every odd
composite number can be expressed as: prime + 2*square.

The solution implements a prime sieve combined with a direct test of Goldbach's
conjecture for each odd composite number encountered. For each candidate, we check
if it can be expressed as p + 2*n² for some prime p and integer n.

Key concepts:
- Prime number generation using a sieve approach
- Composite number identification
- Testing mathematical conjectures
- Number theory and Goldbach's conjecture
- Efficient prime factorization algorithms
"""
import textwrap

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# List of test cases for this problem
# For this problem, no additional input parameters are needed
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},  # No input parameters required for this problem
        answer=5777,  # The expected result (smallest odd composite that disproves Goldbach's conjecture)
    ),
]


def solution() -> int:
    """Find the smallest odd composite number that disproves Goldbach's conjecture.

    Goldbach's conjecture states that every odd composite number can be written as
    the sum of a prime and twice a square number: n = p + 2*s²

    This function:
    1. Generates prime numbers using a sieve approach
    2. For each odd composite number encountered, tests if it can be written as p + 2*s²
    3. Returns the first odd composite that fails this test

    The algorithm combines prime generation with conjecture testing in a single loop:
    - If a number is not marked as composite, it's prime
    - If a number is marked as composite and odd, test Goldbach's conjecture
    - For each composite, update the sieve for future composites

    Returns:
        The smallest odd composite number that cannot be written as a prime plus twice a square

    Raises:
        ValueError: If no solution is found (should not occur for this problem)
    """
    primes, known_composites = set(), dict()
    current_number = 1
    while current_number := current_number + 1:
        if current_number not in known_composites:  # is a new prime
            primes.add(current_number)
            known_composites[current_number * current_number] = [current_number]  # Eratosthene's seive
        else:
            if current_number % 2 != 0:  # is odd composite
                # check half of current number minus all smaller prime is a perfect square
                if not any((((current_number - p) / 2) ** 0.5) % 1 == 0 for p in primes if current_number > p != 2):
                    return current_number
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
    else:
        raise ValueError('No solution found') 


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 46: Goldbach's Other Conjecture
https://projecteuler.net/problem=46

Problem Description:
It was proposed by Christian Goldbach that every odd composite number can be written as the sum of a prime and twice a square.
9 = 7 + 2 * 1^2
15 = 7 + 2 * 2^2
21 = 3 + 2 * 3^2
25 = 7 + 2 * 3^2
27 = 19 + 2 * 2^2
33 = 31 + 2 * 1^2
It turns out that the conjecture was false.
What is the smallest odd composite that cannot be written as the sum of a prime and twice a square?

Approach:
1. Prime Generation and Identification:
   - We implement a modified Sieve of Eratosthenes to efficiently generate primes
   - Rather than using a boolean array, we use a dictionary to track composites
   - For each prime p, we mark p² and its multiples as composite

2. Conjecture Testing:
   - For each odd composite number n, we need to determine if there exists a prime p and integer s
     such that n = p + 2*s²
   - Rearranging: s = sqrt((n-p)/2), so we check if (n-p)/2 is a perfect square
   - We try all primes p < n (except p=2 for odd n) and check if (n-p)/2 is a perfect square

3. Algorithm Integration:
   - We combine prime generation and conjecture testing in a single loop
   - For each number, we either:
     a) Identify it as prime and use it to mark future composites, or
     b) Identify it as composite, test the conjecture if it's odd, and update the sieve

Optimization Techniques:
- We only need to store the prime factors of each composite in our sieve, not all its divisors
- For each composite, we know its smallest prime factor and can use this for efficient marking
- We use the property that (n-p)/2 must be a perfect square to quickly test the conjecture
- The algorithm avoids generating all primes in advance, testing as we go

Mathematical Insights:
- Goldbach's other conjecture (different from his more famous conjecture about even numbers)
  was proposed in 1752 and concerns odd composite numbers
- The disproof of this conjecture is actually a significant result in number theory
- The solution 5777 cannot be written as p + 2*s² for any prime p and integer s

Time Complexity: O(N*sqrt(N)*log(N)) where N is the solution value, as we perform primality
testing and conjecture checking up to the solution.

Space Complexity: O(sqrt(N)*log(N)) for storing primes and composite factors up to the solution.
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
