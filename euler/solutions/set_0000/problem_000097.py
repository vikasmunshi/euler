#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 97:

Problem Statement:
The first known prime found to exceed one million digits was discovered in 1999, and is a Mersenne prime of the form
2^6972593 - 1; it contains exactly 2\,098\,960 digits. Subsequently other Mersenne primes, of the form 2^p - 1,
have been found which contain more digits.

However, in 2004 there was found a massive non-Mersenne prime which contains 2\,357\,207 digits: 28433 × 2^7830457 + 1.

Find the last ten digits of this prime number.

Solution Approach:
The problem requires finding the last 10 digits of a very large number (28433 × 2^7830457 + 1). Computing the entire
number is impractical due to its size (over 2.3 million digits). Instead, we use modular arithmetic to efficiently
calculate only the last 10 digits.

Key principles:
1. We only need to track the last 10 digits during calculation, so we can use modulo 10^10 at each step
2. We calculate 2^7830457 (mod 10^10) using repeated squaring and modular reduction
3. We multiply this result by 28433 and add 1 (mod 10^10) to get the final answer

This approach has O(log n) time complexity rather than O(n) that would be required for naive exponentiation.

Test Cases:
- 28433 × 2^7830457 + 1 (last 10 digits): 8739992577

URL: https://projecteuler.net/problem=97
Answer: 8739992577
"""
from typing import List

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=97)
problem_number: int = 97

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'prime': '28433 × 2^7830457 + 1', 'num_digits': 10}, answer=8739992577, ),
]


# Register this function as a solution for problem #97 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def last_10_digits(*, prime: str, num_digits: int) -> int:
    """
    Calculate the last n digits of a large prime number of form 'a × 2^b + 1'.

    This function efficiently computes the last digits of a large number without
    calculating the entire number, using modular arithmetic properties. For each
    step of the exponentiation, we only need to keep track of the remainder when
    divided by 10^num_digits.

    Args:
        prime: String representation of the prime in the format 'a × 2^b + 1'
        num_digits: Number of last digits to calculate (e.g., 10 for last ten digits)

    Returns:
        int: The last num_digits digits of the calculated prime number

    Example:
        last_10_digits(prime='28433 × 2^7830457 + 1', num_digits=10) -> 8739992577
    """
    # Calculate 10^num_digits, which will be used as the modulus
    divisor: int = 10 ** num_digits

    # Parse the prime formula from the string representation
    prime_parts: List[str] = prime.split()
    number: int
    exponent: int
    number, exponent = int(prime_parts[0]), int(prime_parts[2][2:])  # Extract coefficient and exponent

    # Calculate (number * 2^exponent) % divisor using iterative approach
    # This is more efficient than calculating the full power first
    # Note: For even larger exponents, a binary exponentiation algorithm (square-and-multiply)
    # would be more efficient with O(log n) complexity instead of O(n)
    for _ in range(exponent):
        number *= 2
        number %= divisor  # Take modulus at each step to keep the number manageable

    # Add 1 and take modulus again for the final result
    number += 1
    number %= divisor

    return number


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
