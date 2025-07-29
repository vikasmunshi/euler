#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 87: prime_power_triples

Problem Statement:
  The smallest number expressible as the sum of a prime square, prime cube, and
  prime fourth power is 28. In fact, there are exactly four numbers below fifty
  that can be expressed in such a way: \begin{align} 28 &= 2^2 + 2^3 + 2^4\\ 33 &=
  3^2 + 2^3 + 2^4\\ 49 &= 5^2 + 2^3 + 2^4\\ 47 &= 2^2 + 3^3 + 2^4 \end{align} How
  many numbers below fifty million can be expressed as the sum of a prime square,
  prime cube, and prime fourth power?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=87
Answer: None
"""
from __future__ import annotations

from math import sqrt
from typing import Generator, Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.maths.primes import gen_primes_sundaram_sieve
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=4,
        is_main_case=False,
        kwargs={'max_num': 50},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1097343,
        is_main_case=False,
        kwargs={'max_num': 50000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #87
@register_solution(problem_number=87, test_cases=test_cases)
def prime_power_triples(*, max_num: int) -> int:
    """Count numbers below max_num that can be expressed as sum of prime², prime³, and prime⁴.

    This function systematically generates all possible sums of the form p²+q³+r⁴ where
    p, q, and r are prime numbers, and counts the unique sums below max_num.

    Args:
        max_num: The upper limit for the sums to consider

    Returns:
        The count of unique numbers below max_num expressible as sum of prime², prime³, and prime⁴
    """
    # Generate primes up to √(max_num) - sufficient for our calculations
    primes: Tuple[int, ...] = gen_primes_sundaram_sieve(max_limit=int(sqrt(max_num)))

    # Set to store unique sums
    numbers = set()

    # Calculate upper bounds for partial sums to enable early breaking
    # Maximum value for prime⁴ + prime³ = max_num - smallest prime²
    max_quadruple_cube: int = max_num - 4  # 4 is 2²
    # Maximum value for prime⁴ = max_num - smallest prime³ - smallest prime²
    max_quadruple: int = max_quadruple_cube - 8  # 8 is 2³

    # Iterate through prime fourth powers (p⁴)
    for quadruple in prime_powers(primes, 4):
        if quadruple > max_quadruple:
            break  # Early termination if fourth power exceeds limit

        # Iterate through prime cubes (q³)
        for cube in prime_powers(primes, 3):
            # Calculate partial sum p⁴ + q³
            if (quadruple_cube := quadruple + cube) > max_quadruple_cube:
                break  # Early termination if partial sum exceeds limit

            # Iterate through prime squares (r²)
            for square in prime_powers(primes, 2):
                # Calculate full sum p⁴ + q³ + r²
                if (number := quadruple_cube + square) >= max_num:
                    break  # Early termination if sum exceeds or equals max_num

                # Add valid sum to our set of unique numbers
                numbers.add(number)

    # Return the count of unique numbers found
    return len(numbers)


def prime_powers(primes: Tuple[int, ...], exponent: int) -> Generator[int, None, None]:
    """Generate prime powers by raising each prime to the given exponent.

    Args:
        primes: A tuple of prime numbers to use as bases
        exponent: The power to raise each prime to

    Yields:
        Each prime raised to the specified power in ascending order
    """
    for base in primes:
        yield base ** exponent


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(87))
