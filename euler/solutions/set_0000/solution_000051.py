#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 51: prime_digit_replacements

Problem Statement:
  By replacing the 1st digit of the 2-digit number *3, it turns out that six of
  the nine possible values: 13, 23, 43, 53, 73, and 83, are all prime. By
  replacing the 3rd and 4th digits of 56**3 with the same digit, this 5-digit
  number is the first example having seven primes among the ten generated numbers,
  yielding the family: 56003, 56113, 56333, 56443, 56663, 56773, and 56993.
  Consequently 56003, being the first member of this family, is the smallest prime
  with this property. Find the smallest prime which, by replacing part of the
  number (not necessarily adjacent digits) with the same digit, is part of an
  eight prime value family.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=51
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sundaram_sieve, is_prime
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=13,
        is_main_case=False,
        kwargs={'num_digits': 6, 'prime_run': 6},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=56003,
        is_main_case=False,
        kwargs={'num_digits': 6, 'prime_run': 7},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=121313,
        is_main_case=False,
        kwargs={'num_digits': 6, 'prime_run': 8},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #51
@register_solution(problem_number=51, test_cases=test_cases)
def prime_digit_replacements(*, num_digits: int, prime_run: int) -> int:
    """
    Find the smallest prime that forms a family of prime numbers by digit replacement.

    This solution finds prime numbers where replacing specific digits with other digits
    yields a family of prime numbers of the specified size. It systematically examines
    primes in ascending order and tests various digit replacement patterns until finding
    a prime that belongs to a family of the required size.

    Args:
        prime_run: The required number of primes in the family (e.g., 6, 7, or 8)
        num_digits: The maximum number of digits to consider (default: 6)

    Returns:
        The smallest prime that generates a family of 'prime_run' primes

    Examples:
        >>> prime_digit_replacements(prime_run=6)
        13  # Family: 13,23,43,53,73,83
        >>> prime_digit_replacements(prime_run=7)
        56003  # Family includes 56003,56113,56333,etc.
        >>> prime_digit_replacements(prime_run=8)
        121313  # The answer to the main problem

    Raises:
        ValueError: If no solution is found within the given constraints
    """
    # Generate prime numbers up to the specified limit
    for prime in gen_primes_sundaram_sieve(max_limit=10 ** num_digits):
        # For each digit that can be replaced (we can only replace with digits that would create 'prime_run' primes)
        # We only need to check digits '0' through '9'-(prime_run) because we need 'prime_run' valid replacements
        for replaced in '0123456789'[:10 - prime_run]:
            # Create a sequence of primes by replacing the digit and checking if each result is prime.
            # To avoid duplicates, we only consider replacements with digits >= the original digit,
            # and we only include numbers that are >= the original prime to ensure we find the smallest prime
            sequence = tuple(new_prime for replacement in '0123456789' if replacement >= replaced
                             if (new_prime := int(str(prime).replace(replaced, replacement))) >= prime
                             and is_prime(new_prime))
            # If we found exactly 'prime_run' primes in the family, return the original prime
            if len(sequence) == prime_run:
                return prime
    else:
        # If we've exhausted all primes up to the limit without finding a solution
        raise ValueError('No solution found')


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(51))
