#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 27
# https://projecteuler.net/problem=27
# Answer: answers={1000: -59231}
# Notes: Finding the coefficients for a quadratic formula that produces the most consecutive primes
import textwrap

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
    Find the product of coefficients a and b in the quadratic formula n² + an + b
    that produces the maximum number of consecutive primes for n starting from 0.

    The function explores different coefficient combinations to find the one that
    generates the longest sequence of primes when plugged into the formula n² + an + b.

    Strategy:
    1. For coefficient b: Since the formula must produce a prime when n=0, b must be prime
    2. For coefficient a: We test odd values (and 0 when b=2) to explore valid candidates
    3. For each (a,b) combination, we check four sign variations: (a,b), (a,-b), (-a,-b), (-a,b)
    4. We track the length of the prime sequence and the product of coefficients
    5. Return the product of the coefficients that generate the longest sequence

    Args:
        max_limit: The maximum absolute value for coefficients a and b

    Returns:
        The product of coefficients a and b that produces the maximum number of
        consecutive primes
    """
    return max([
        max((prime_run(a, b), a * b),  # Test (a, b) combination
            (prime_run(a, -b), -a * b),  # Test (a, -b) combination
            (prime_run(-a, -b), a * b),  # Test (-a, -b) combination
            (prime_run(-a, b), -a * b))  # Test (-a, b) combination
        for b in gen_primes_sundaram_sieve(max_limit=max_limit)  # b must be prime
        for a in range(0 if b == 2 else 1, max_limit, 2)  # a should be odd (or 0 when b=2)
    ])[1]  # Return the product of coefficients (second element of tuple)


# Explicitly annotate that this function implements SolutionProtocol
solution: SolutionProtocol

# Preserve the original problem description in the docstring
solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 27
https://projecteuler.net/problem=27
Euler discovered the remarkable quadratic formula:
n^2 + n + 41
It turns out that the formula will produce 40 primes for the consecutive integer values 0 <= n <= 39.
However, when n = 40, 40^2 + 40 + 41 = 40(40 + 1) + 41 is divisible by 41,
and certainly when n = 41, 41^2 + 41 + 41 is clearly divisible by 41.
The incredible formula n^2 - 79n + 1601 was discovered, which produces 80 primes for the consecutive values 0 <= n <= 79.
The product of the coefficients, -79 and 1601, is -126479.
Considering quadratics of the form:

n^2 + an + b, where |a| where |n| is the modulus/absolute value of n
e.g. |11| = 11 and |-4| = 4

Find the product of the coefficients, a and b, for the quadratic expression that produces the maximum number of
primes for consecutive values of n, starting with n = 0.

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
