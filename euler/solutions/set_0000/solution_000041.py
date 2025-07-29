#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 41: pandigital_prime

Problem Statement:
  We shall say that an n-digit number is pandigital if it makes use of all the
  digits 1 to n exactly once. For example, 2143 is a 4-digit pandigital and is
  also prime. What is the largest n-digit pandigital prime that exists?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=41
Answer: None
"""
from __future__ import annotations

from itertools import permutations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import is_prime
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=7652413,
        is_main_case=False,
        kwargs={},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #41
@register_solution(problem_number=41, test_cases=test_cases)
def pandigital_prime() -> int:
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
        >>> pandigital_prime()
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
    raise SystemExit(evaluate_solutions(41))
