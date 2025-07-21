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

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=7)
problem_number: int = 7

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'n': 6}, answer=13, ),  # Find the 6th prime number - 13
    ProblemArgs(kwargs={'n': 10001}, answer=104743, ),  # Find the 10001st prime number - 104743
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def nth_prime_number(*, n: int) -> int:
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
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
