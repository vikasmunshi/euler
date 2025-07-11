# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 10: Summation of Primes

Problem Statement:
The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.
Find the sum of all the primes below two million.

Solution Approach:
This solution leverages the Sieve of Sundaram algorithm to efficiently generate prime numbers:

1. Sieve Algorithm: The solution utilizes the `gen_primes_sundaram_sieve` function from the
   project's prime number utility module. This function implements the Sieve of Sundaram,
   an efficient algorithm for generating all prime numbers up to a specified limit.

2. Memory Efficiency: The Sieve of Sundaram is more memory-efficient than the classic
   Sieve of Eratosthenes because it only needs to track odd numbers.

3. Implementation Details: The sieve works by:
   - Transforming the problem of finding primes up to n to finding numbers that, when
     doubled and incremented by 1, give primes
   - Marking numbers of the form i+j+2ij as composite
   - Converting remaining numbers k to 2k+1 to get the actual primes
   - Adding 2 separately (since it's the only even prime)

4. Caching: The prime generation function uses intelligent caching to avoid regenerating
   prime numbers that have already been computed in previous runs.

The overall approach is optimal for this problem because it efficiently generates all primes
below the limit and simply sums them, avoiding the need to individually test each number for
primality.

Test Cases:
- For max_num=10: Sum = 17 (2+3+5+7)
- For max_num=2000000: Sum = 142913828922

URL: https://projecteuler.net/problem=10
Answer: 142913828922
"""
from euler.primes import gen_primes_sundaram_sieve
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_num': 10}, answer=17, ),
    ProblemArgs(kwargs={'max_num': 2000000}, answer=142913828922, ),
]


def solution(*, max_num: int) -> int:
    """
    Calculate the sum of all prime numbers below a given limit.

    This function generates all prime numbers below the specified limit using the
    Sieve of Sundaram algorithm, then calculates their sum.

    Args:
        max_num: The upper limit (exclusive) for prime numbers to include in the sum

    Returns:
        The sum of all prime numbers less than max_num

    Examples:
        >>> solution(max_num=10)
        17  # Sum of 2, 3, 5, and 7
        >>> solution(max_num=2000000)
        142913828922

    Time Complexity: O(n log log n) where n is max_num, due to the sieve algorithm
    Space Complexity: O(n) for storing the prime numbers
    """
    return sum(gen_primes_sundaram_sieve(max_limit=max_num))


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
