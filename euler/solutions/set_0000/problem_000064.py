# !/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Solution to Project Euler problem 64: Odd period square roots

Problem Statement:
All square roots are periodic when written as continued fractions and can be written in the form:

√N = a₀ + 1/(a₁ + 1/(a₂ + 1/(a₃ + ...)))

For example, let us consider √23:
√23 = 4 + √23 - 4 = 4 + 1/(1/(√23 - 4)) = 4 + 1/(1 + (√23 - 3)/7)

If we continue we would get the following expansion:
√23 = 4 + 1/(1 + 1/(3 + 1/(1 + 1/(8 + ...))))

The process can be summarised as follows:
a₀ = 4, 1/(√23 - 4) = (√23 + 4)/7 = 1 + (√23 - 3)/7
a₁ = 1, 7/(√23 - 3) = 7(√23 + 3)/14 = 3 + (√23 - 3)/2
a₂ = 3, 2/(√23 - 3) = 2(√23 + 3)/14 = 1 + (√23 - 4)/7
a₃ = 1, 7/(√23 - 4) = 7(√23 + 4)/7 = 8 + √23 - 4
a₄ = 8, 1/(√23 - 4) = (√23 + 4)/7 = 1 + (√23 - 3)/7

It can be seen that the sequence is repeating. For conciseness, we use the notation
√23 = [4;(1,3,1,8)], to indicate that the block (1,3,1,8) repeats indefinitely.

The first ten continued fraction representations of (irrational) square roots are:
√2 = [1;(2)], period=1
√3 = [1;(1,2)], period=2
√5 = [2;(4)], period=1
√6 = [2;(2,4)], period=2
√7 = [2;(1,1,1,4)], period=4
√8 = [2;(1,4)], period=2
√10 = [3;(6)], period=1
√11 = [3;(3,6)], period=2
√12 = [3;(2,6)], period=2
√13 = [3;(1,1,1,1,6)], period=5

Exactly four continued fractions, for N ≤ 13, have an odd period.
How many continued fractions for N ≤ 10,000 have an odd period?

Solution Approach:
This solution applies number theory concepts related to continued fractions for quadratic irrationals.
For each non-square number up to the specified limit, we:

1. Calculate the continued fraction representation using the canonical form algorithm
2. Efficiently detect when the sequence begins to repeat using triplet representation (m, d, a)
3. Determine the period length by counting terms until repetition
4. Count how many of these periods have odd length

The mathematical properties of continued fractions of square roots provide elegant ways to detect
cycles. We use the fact that all continued fractions for square roots follow a pattern where
the sequence of partial quotients becomes periodic, and we can detect this periodicity by
tracking state transformations in our algorithm.

An interesting mathematical fact: Lagrange proved that the continued fraction of a number is
periodic if and only if the number is a quadratic irrational (like square roots of non-square
integers).

Test Cases:
- For N ≤ 13: There are 4 numbers with odd period lengths (√2, √3, √5, and √13)
- For N ≤ 10,000: We need to determine this count (answer: 1322)

URL: https://projecteuler.net/problem=64
Answer: 1322
"""
from math import isqrt, sqrt

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=64)
problem_number: int = 64

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_limit': 13}, answer=4, ),
    ProblemArgs(kwargs={'max_limit': 10000}, answer=1322, ),
]


def get_period_length(n: int) -> int:
    """
    Calculate the period length of the continued fraction representation of √n.

    This function implements the standard algorithm for computing the continued fraction
    expansion of a quadratic irrational number, specifically square roots. It uses the
    canonical form representation with triplets (m, d, a) to efficiently detect cycles.

    Algorithm Details:
    1. Initialize with values derived from the integer square root of n
    2. Iteratively compute the next terms in the sequence using the recurrence relations:
       - m = d * a - m
       - d = (n - m^2) / d
       - a = (a0 + m) / d
    3. Store each computed triplet (m, d, a) and check for repetition
    4. Return the length of the sequence before repetition, which equals the period length

    Args:
        n: The number whose square root will be expanded as a continued fraction
           (must be a positive integer that is not a perfect square)

    Returns:
        The period length of the continued fraction representation

    References:
        - https://en.wikipedia.org/wiki/Periodic_continued_fraction#Canonical_form_and_repetend
    """
    a0 = a = isqrt(n)
    d, m, p = 1, 0, []
    while True:
        m = d * a - m
        d = (n - m ** 2) // d
        a = (a0 + m) // d
        if (m, d, a) in p:
            break
        p.append((m, d, a))
    return len(p)


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def count_continued_fractions_of_sqrt_2_with_odd_period(*, max_limit: int) -> int:
    """
    Count the number of continued fractions for square roots of integers up to max_limit that have an odd period.

    This solution computes the continued fraction representation of square roots for each non-perfect
    square number up to the given limit. It then determines which of these representations have an odd
    period length, using an efficient cycle detection algorithm.

    Mathematical Background:
    - For an irrational square root √N, its continued fraction can be represented as [a₀; a₁, a₂, ...]
    - The sequence of terms after a₀ is always periodic for quadratic irrationals like square roots
    - For each number, we calculate the period length using the get_period_length helper function
    - We then count how many of these period lengths are odd

    Implementation Details:
    - We skip perfect squares as they have terminating (non-periodic) continued fractions
    - We use a generator expression with sum() for a concise and efficient implementation
    - The algorithm is based on fundamental properties of continued fractions for quadratic irrationals

    Args:
        max_limit: The upper bound for N, where we check square roots of integers from 2 to max_limit

    Returns:
        The count of numbers with odd-period continued fraction representations

    Complexity:
        Time: O(max_limit * log(max_limit)) - we process each number and the period detection
              is logarithmic in the value of the number
        Space: O(log(max_limit)) - storage for the period sequence of each number

    Examples:
        >>> count_continued_fractions_of_sqrt_2_with_odd_period(max_limit=13)
        4  # √2, √3, √5, and √13 have odd periods

        >>> count_continued_fractions_of_sqrt_2_with_odd_period(max_limit=10000)
        1322  # Total count for all numbers up to 10,000
    """

    return sum(get_period_length(n) % 2 == 1 for n in range(2, max_limit + 1) if not sqrt(n).is_integer())


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
