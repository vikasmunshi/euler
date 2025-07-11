# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 7: 10001st Prime

Problem Statement:
By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that the 6th prime is 13.
What is the 10,001st prime number?

Solution Approach:
This solution employs a modified version of the Sieve of Eratosthenes algorithm, optimized for
finding the nth prime number efficiently. The implementation includes several key optimizations:

1. Prime Number Theorem: Uses the Prime Number Theorem to estimate an upper bound for the
   search space. The theorem states that the nth prime is approximately n*ln(n), which helps
   avoid allocating an unnecessarily large sieve.

2. Odd Number Optimization: Only considers odd numbers (except for handling 2 as a special case),
   reducing the search space by half.

3. Index Mapping: Uses a clever indexing scheme where the index i in the sieve array corresponds
   to the odd number 2i+1, making the algorithm more space-efficient.

4. Composite Number Generation: Uses the formula i+j+(2*i*j) to generate indices of composite
   numbers, which is a mathematical optimization specific to this implementation.

The algorithm has a time complexity of approximately O(n log log n), which is efficient
even for finding large prime numbers like the 10,001st prime.

Test Cases:
- For n=6: 13 (the 6th prime number)
- For n=10001: 104743 (the 10,001st prime number)

URL: https://projecteuler.net/problem=7
Answer: 104743
"""
from math import log

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 6}, answer=13, ),  # Find the 6th prime number - 13
    ProblemArgs(kwargs={'n': 10001}, answer=104743, ),  # Find the 10001st prime number - 104743
]


def solution(*, n: int) -> int:
    """
    Find the nth prime number.

    This implementation uses a modified Sieve of Eratosthenes optimized for finding
    the nth prime number. It specifically focuses on odd numbers, since all even numbers
    except 2 are composite.

    Args:
        n: The position of the prime number to find (e.g., n=6 finds the 6th prime)

    Returns:
        The nth prime number

    Note:
        - For n=1, we return 2 (the first prime number) as a special case
        - For n>1, we search through odd numbers using the sieve method
        - The formula i+j+(2*i*j) generates indices of composite numbers
    """
    # Handle special case: the first prime number is 2
    if n == 1:
        return 2

    # Estimate the upper bound for the nth prime using Prime Number Theorem
    max_expected_value = int(n * log(n))

    # Initialize the sieve array where index i corresponds to number 2i+1
    numbers = list(range(0, max_expected_value + 1))

    # Apply the sieve algorithm to mark composite numbers
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + (2 * i * j)] = 0  # mark n where 2n+1 is not prime as 0
            except IndexError:
                break

    # Extract all non-zero values (representing prime indices)
    # Convert back to actual prime numbers using the formula 2i+1
    # Select the (n-2)th element (accounting for the fact that we've excluded 2,
    # and our indexing starts at 0)
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


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
