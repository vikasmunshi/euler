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
from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import gen_primes_sundaram_sieve

# The problem number from Project Euler (https://projecteuler.net/problem=10)
problem_number: int = 10

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_num': 10}, answer=17, ),
    ProblemArgs(kwargs={'max_num': 2000000}, answer=142913828922, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def sum_primes(*, max_num: int) -> int:
    """
    Calculate the sum of all prime numbers below a given limit.

    This function generates all prime numbers below the specified limit using the
    Sieve of Sundaram algorithm, then calculates their sum.

    Args:
        max_num: The upper limit (exclusive) for prime numbers to include in the sum

    Returns:
        The sum of all prime numbers less than max_num

    Examples:
        >>> sum_primes(max_num=10)
        17  # Sum of 2, 3, 5, and 7
        >>> sum_primes(max_num=2000000)
        142913828922

    Time Complexity: O(n log log n) where n is max_num, due to the sieve algorithm
    Space Complexity: O(n) for storing the prime numbers
    """
    return sum(gen_primes_sundaram_sieve(max_limit=max_num))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
