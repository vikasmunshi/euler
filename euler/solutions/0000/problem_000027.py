#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 27: Quadratic primes

Problem Statement:
Euler discovered the remarkable quadratic formula:
n² + n + 41

It turns out that the formula will produce 40 primes for the consecutive integer values
0 ≤ n ≤ 39. However, when n = 40, 40² + 40 + 41 = 40(40 + 1) + 41 is divisible by 41,
and certainly when n = 41, 41² + 41 + 41 is clearly divisible by 41.

The incredible formula n² - 79n + 1601 was discovered, which produces 80 primes for the
consecutive values 0 ≤ n ≤ 79. The product of the coefficients, -79 and 1601, is -126479.

Considering quadratics of the form:
n² + an + b, where |a| < 1000 and |b| < 1000

where |n| is the modulus/absolute value of n
e.g. |11| = 11 and |-4| = 4

Find the product of the coefficients, a and b, for the quadratic expression that produces
the maximum number of primes for consecutive values of n, starting with n = 0.

Solution Approach:
This implementation systematically tests different coefficient combinations to find the one
that generates the longest sequence of primes. Key optimizations include:

1. For coefficient b: Since n²+an+b must produce a prime when n=0, b itself must be prime
2. For coefficient a: Testing odd values (and 0 when b=2) to explore valid candidates
3. For each (a,b) pair, checking all four sign variations: (a,b), (a,-b), (-a,-b), (-a,b)
4. Using efficient primality testing to count consecutive primes for each formula

Test Cases:
- For max_limit=1000, the answer is -59231

URL: https://projecteuler.net/problem=27
Answer: -59231
"""

from euler.primes import gen_primes_sundaram_sieve, is_prime
from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

# Define test cases with expected answers
problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_limit': 1000},  # Search for coefficients with absolute values < 1000
        answer=-59231,  # Expected product of the coefficients
    ),
]


def prime_run(a: int, b: int) -> int:
    """
    Calculate the number of consecutive primes produced by the quadratic formula n² + an + b.

    This function computes how many consecutive integers, starting from n=0,
    will produce prime numbers when substituted into the quadratic formula n² + an + b.

    Args:
        a: The coefficient of the linear term in the quadratic formula
        b: The constant term in the quadratic formula

    Returns:
        The count of consecutive primes generated starting from n=0

    Examples:
        >>> prime_run(1, 41)  # For n²+n+41
        40
        >>> prime_run(-79, 1601)  # For n²-79n+1601
        80
    """
    x = 0
    while is_prime(abs(x ** 2 + a * x + b)):
        x += 1
    return x


def solution(*, max_limit: int) -> int:
    """
    Find the product of coefficients a and b that produces the maximum number of
    consecutive primes in the quadratic formula n² + an + b.

    This solution examines various coefficient combinations to find the quadratic
    formula that generates the longest sequence of prime numbers for consecutive
    values of n starting from 0.

    Args:
        max_limit: The maximum absolute value for coefficients a and b

    Returns:
        The product of the coefficients a and b that produces the maximum number
        of consecutive primes

    Example:
        >>> solution(max_limit=1000)
        -59231  # The product of coefficients that produces the longest prime sequence
    """
    return max([
        max((prime_run(a, b), a * b),  # Test (a, b) combination
            (prime_run(a, -b), -a * b),  # Test (a, -b) combination
            (prime_run(-a, -b), a * b),  # Test (-a, -b) combination
            (prime_run(-a, b), -a * b))  # Test (-a, b) combination
        for b in gen_primes_sundaram_sieve(max_limit=max_limit)  # b must be prime
        for a in range(0 if b == 2 else 1, max_limit, 2)  # a should be odd (or 0 when b=2)
    ])[1]  # Return the product of coefficients (second element of tuple)


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
