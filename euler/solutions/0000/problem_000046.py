#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 46: Goldbach's other conjecture

Problem Statement:
It was proposed by Christian Goldbach that every odd composite number can be written as 
the sum of a prime and twice a square.

9 = 7 + 2 × 1²
15 = 7 + 2 × 2²
21 = 3 + 2 × 3²
25 = 7 + 2 × 3²
27 = 19 + 2 × 2²
33 = 31 + 2 × 1²

It turns out that the conjecture was false.

What is the smallest odd composite that cannot be written as the sum of a prime and twice a square?

Solution Approach:
This solution systematically tests Goldbach's conjecture by:
1. Generating prime numbers using a sieve of Eratosthenes approach
2. For each odd composite number encountered, testing if it can be expressed as p + 2s²
   by checking all primes less than the number
3. Returning the first odd composite that can't be expressed in this form

The algorithm efficiently combines prime number generation with conjecture testing in a
single loop, avoiding the need to generate all primes upfront.

Test Cases:
- The examples in the problem statement confirm that 9, 15, 21, 25, 27, and 33 all satisfy the conjecture
- The answer is 5777, which is the first odd composite that disproves the conjecture

URL: https://projecteuler.net/problem=46
Answer: 5777
"""

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={},  # No input parameters required for this problem
        answer=5777,  # The expected result (smallest odd composite that disproves Goldbach's conjecture)
    ),
]


def solution() -> int:
    """
    Find the smallest odd composite number that disproves Goldbach's conjecture.

    This solution searches for the first counterexample to Goldbach's conjecture, which
    states that every odd composite number can be expressed as the sum of a prime and
    twice a square (n = p + 2s²). The algorithm efficiently generates primes and tests
    each odd composite number against all smaller primes.

    Returns:
        The smallest odd composite number that cannot be expressed as p + 2s²

    Example:
        >>> solution()
        5777

    Note:
        The algorithm uses a modified sieve of Eratosthenes approach to efficiently
        generate prime numbers while simultaneously testing odd composite numbers
        against the conjecture.
    """
    primes: Set[int] = set()
    known_composites: Dict[int, List[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:  # is a new prime
            primes.add(current_number)
            known_composites[current_number ** 2] = [current_number]  # Eratosthene's seive
        else:
            if current_number % 2 != 0:  # is odd composite
                # check half of current number minus all smaller prime is a perfect square
                if not any((((current_number - p) / 2) ** 0.5) % 1 == 0 for p in primes if current_number > p != 2):
                    return current_number
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
        current_number += 1


if __name__ == '__main__':
    # This block is executed when the Python module is run directly.
    # It evaluates the solution function to ensure its correctness against test cases.

    # Importing required modules: `module_main` manages how the solution is invoked and tested,
    # while `cast` helps with type safety in passing the solution as a `SolutionProtocol`.
    from typing import cast, Set, Dict, List
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
