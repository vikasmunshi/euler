#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 64: odd_period_square_roots

Problem Statement:
  All square roots are periodic when written as continued fractions and can be
  written in the form:  \displaystyle \quad \quad \sqrt{N}=a_0+\frac 1 {a_1+\frac
  1 {a_2+ \frac 1 {a_3+ ...}}}  For example, let us consider \sqrt{23}: \quad
  \quad \sqrt{23}=4+\sqrt{23}-4=4+\frac 1 {\frac 1 {\sqrt{23}-4}}=4+\frac 1
  {1+\frac{\sqrt{23}-3}7}  If we continue we would get the following expansion:
  \displaystyle \quad \quad \sqrt{23}=4+\frac 1 {1+\frac 1 {3+ \frac 1 {1+\frac 1
  {8+ ...}}}}  The process can be summarised as follows:  \quad \quad a_0=4, \frac
  1 {\sqrt{23}-4}=\frac {\sqrt{23}+4} 7=1+\frac {\sqrt{23}-3} 7 \quad \quad a_1=1,
  \frac 7 {\sqrt{23}-3}=\frac {7(\sqrt{23}+3)} {14}=3+\frac {\sqrt{23}-3} 2 \quad
  \quad a_2=3, \frac 2 {\sqrt{23}-3}=\frac {2(\sqrt{23}+3)} {14}=1+\frac
  {\sqrt{23}-4} 7 \quad \quad a_3=1, \frac 7 {\sqrt{23}-4}=\frac {7(\sqrt{23}+4)}
  7=8+\sqrt{23}-4 \quad \quad a_4=8, \frac 1 {\sqrt{23}-4}=\frac {\sqrt{23}+4}
  7=1+\frac {\sqrt{23}-3} 7 \quad \quad a_5=1, \frac 7 {\sqrt{23}-3}=\frac {7
  (\sqrt{23}+3)} {14}=3+\frac {\sqrt{23}-3} 2  \quad \quad a_6=3, \frac 2
  {\sqrt{23}-3}=\frac {2(\sqrt{23}+3)} {14}=1+\frac {\sqrt{23}-4} 7 \quad \quad
  a_7=1, \frac 7 {\sqrt{23}-4}=\frac {7(\sqrt{23}+4)} {7}=8+\sqrt{23}-4  It can be
  seen that the sequence is repeating. For conciseness, we use the notation
  \sqrt{23}=[4;(1,3,1,8)], to indicate that the block (1,3,1,8) repeats
  indefinitely. The first ten continued fraction representations of (irrational)
  square roots are:  \quad \quad \sqrt{2}=[1;(2)], period=1 \quad \quad
  \sqrt{3}=[1;(1,2)], period=2 \quad \quad \sqrt{5}=[2;(4)], period=1 \quad \quad
  \sqrt{6}=[2;(2,4)], period=2 \quad \quad \sqrt{7}=[2;(1,1,1,4)], period=4 \quad
  \quad \sqrt{8}=[2;(1,4)], period=2 \quad \quad \sqrt{10}=[3;(6)], period=1 \quad
  \quad \sqrt{11}=[3;(3,6)], period=2 \quad \quad \sqrt{12}=[3;(2,6)], period=2
  \quad \quad \sqrt{13}=[3;(1,1,1,1,6)], period=5  Exactly four continued
  fractions, for N \le 13, have an odd period. How many continued fractions for N
  \le 10\,000 have an odd period?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=64
Answer: None
"""
from __future__ import annotations

from math import isqrt, sqrt

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=4,
        is_main_case=False,
        kwargs={'max_limit': 13},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1322,
        is_main_case=False,
        kwargs={'max_limit': 10000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #64
@register_solution(problem_number=64, test_cases=test_cases)
def odd_period_square_roots(*, max_limit: int) -> int:
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
        >>> odd_period_square_roots(max_limit=13)
        4  # √2, √3, √5, and √13 have odd periods

        >>> odd_period_square_roots(max_limit=10000)
        1322  # Total count for all numbers up to 10,000
    """

    return sum(get_period_length(n) % 2 == 1 for n in range(2, max_limit + 1) if not sqrt(n).is_integer())


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


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(64))
