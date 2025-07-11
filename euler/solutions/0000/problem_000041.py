#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 41: Pandigital prime

Problem Statement:
We shall say that an n-digit number is pandigital if it makes use of all the digits 1 to n exactly once.
For example, 2143 is a 4-digit pandigital and is also prime.

What is the largest n-digit pandigital prime that exists?

Solution Approach:
This solution uses number theory to reduce the search space. Since a number is divisible by 3
if the sum of its digits is divisible by 3, we know that:
- 9-digit pandigitals (sum = 45) are divisible by 3 and thus not prime
- 8-digit pandigitals (sum = 36) are divisible by 3 and thus not prime
- 7-digit pandigitals (sum = 28) could be prime
- 6-digit pandigitals (sum = 21) are divisible by 3 and thus not prime
- 5-digit pandigitals (sum = 15) are divisible by 3 and thus not prime
- 4-digit pandigitals (sum = 10) could be prime

The algorithm generates pandigital numbers in descending order for 7 digits, then 4 digits
if necessary, and tests each for primality until the first (largest) prime is found.

Test Cases:
- The correct answer is 7652413

URL: https://projecteuler.net/problem=41
Answer: 7652413
"""

from itertools import permutations

from euler.primes import is_prime
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=7652413, ),
]


def largest_pandigital_prime() -> int:
    """
    Find the largest n-digit pandigital prime number.

    This solution uses mathematical optimization to efficiently search for the largest
    pandigital prime. By analyzing the divisibility properties of pandigital numbers,
    we can focus our search on only 7-digit and 4-digit pandigitals, since all other
    lengths are divisible by 3 (and thus not prime).

    The algorithm generates pandigital numbers in descending order and tests each for
    primality until the largest prime is found.

    Returns:
        The largest n-digit pandigital prime number

    Example:
        >>> largest_pandigital_prime()
        7652413
    """
    pandigital_primes = (
        number
        for length in (7, 4)  # all other length pandigital numbers are divisible by 3
        for number in (int(''.join(digits)) for digits in permutations(reversed('123456789'[:length]), length))
        if is_prime(number)
    )
    return next(pandigital_primes)


# Create an alias for the largest_pandigital_prime function to match the expected solution interface
# This allows the function to be named descriptively while still conforming to the
# Project Euler framework's convention of using 'solution' as the entry point
solution = largest_pandigital_prime

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
