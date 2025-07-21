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

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import is_prime

# The problem number from Project Euler (https://projecteuler.net/problem=41)
problem_number: int = 41

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={}, answer=7652413, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
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


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
