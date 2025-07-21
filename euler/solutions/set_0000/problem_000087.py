#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 87:

Problem Statement:
The smallest number expressible as the sum of a prime square, prime cube, and prime fourth power is 28.
In fact, there are exactly four numbers below fifty that can be expressed in such a way:

28 = 2² + 2³ + 2⁴
33 = 3² + 2³ + 2⁴
49 = 5² + 2³ + 2⁴
47 = 2² + 3³ + 2⁴

How many numbers below fifty million can be expressed as the sum of a prime square, prime cube, and prime fourth power?

Solution Approach:
The solution uses a straightforward approach to generate all possible sums of prime squares,
prime cubes, and prime fourth powers up to the given limit (fifty million):

1. Generate a list of prime numbers up to √(max_num), as no prime square component can exceed max_num
2. For each valid combination of prime⁴, prime³, and prime², calculate their sum
3. Add the sum to a set to avoid counting duplicates (since different combinations might yield the same sum)
4. Return the size of the set as the answer

Optimizations:
- We iterate from smallest to largest powers to break early when partial sums exceed the limit
- We calculate upper bounds for each power component to avoid unnecessary calculations
- We use a set to efficiently track unique sums

Test Cases:
- For max_num = 50, we expect 4 distinct numbers (as given in the problem statement)
- For max_num = 50,000,000, we expect 1,097,343 distinct numbers

URL: https://projecteuler.net/problem=87
Answer: 1097343
"""
from math import sqrt
from typing import Generator, Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList
from euler.utils.primes import gen_primes_sundaram_sieve

# The problem number from Project Euler (https://projecteuler.net/problem=87)
problem_number: int = 87

# Define the test cases for validating the solution
problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_num': 50}, answer=4, ),
    ProblemArgs(kwargs={'max_num': 50 * 10 ** 6}, answer=1097343, ),
]


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


# Register this function as a solution for problem #87 with test cases
@register_solution(problem_number=problem_number, args_list=problem_args_list)
def num_of_matching_numbers(*, max_num: int) -> int:
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


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
