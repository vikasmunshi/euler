#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 66: diophantine_equation

Problem Statement:
  Consider quadratic Diophantine equations of the form: x^2 - Dy^2 = 1 For
  example, when D=13, the minimal solution in x is 649^2 - 13 * 180^2 = 1. It can
  be assumed that there are no solutions in positive integers when D is square. By
  finding minimal solutions in x for D = \{2, 3, 5, 6, 7\}, we obtain the
  following: \begin{align} 3^2 - 2 * 2^2 &= 1\\ 2^2 - 3 * 1^2 &= 1\\
  {\color{red}{\mathbf 9}}^2 - 5 * 4^2 &= 1\\ 5^2 - 6 * 2^2 &= 1\\ 8^2 - 7 * 3^2
  &= 1 \end{align} Hence, by considering minimal solutions in x for D \le 7, the
  largest x is obtained when D=5. Find the value of D \le 1000 in minimal
  solutions of x for which the largest value of x is obtained.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=66
Answer: None
"""
from __future__ import annotations

from fractions import Fraction
from math import floor, sqrt
from operator import itemgetter
from typing import Tuple

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase


def compute_nth_convergent(continued_fraction: Tuple[int, ...], n: int) -> Fraction:
    """
    Compute the nth convergent of a continued fraction representation.

    Convergents are rational approximations of a continued fraction, getting progressively closer
    to the actual irrational value. This function computes the nth convergent using the recurrence
    relation for continued fractions, handling the periodic nature of √D's representation.

    Mathematical Background:
    - For a continued fraction [a₀; a₁, a₂, ...], the nth convergent is the rational number
      obtained by truncating the continued fraction at the nth term
    - Convergents alternate between being slightly larger and slightly smaller than the true value
    - For Pell's equation, specific convergents provide the minimal solutions

    Algorithm Details:
    1. Use modular arithmetic to handle the periodic part of the continued fraction
    2. Start with the last term of the truncated continued fraction
    3. Work backwards, applying the recurrence relation: p_n = a_n * p_{n-1} + p_{n-2}
    4. Add the integer part (a₀) at the end

    Args:
        continued_fraction: A tuple where the first element is the integer part (a₀) and
                           subsequent elements form the periodic part of the continued fraction
        n: The index of the convergent to compute (1-based)

    Returns:
        A Fraction object representing the computed convergent
    """
    period_length: int = len(continued_fraction) - 1
    convergent: Fraction = Fraction(continued_fraction[((n - 1) % period_length) + 1], 1)

    for i in range(n - 1, 0, -1):
        term_index = ((i - 1) % period_length) + 1
        term = Fraction(continued_fraction[term_index], 1)
        convergent = term + Fraction(1, convergent)

    convergent = Fraction(continued_fraction[0], 1) + Fraction(1, convergent)
    return convergent


def find_fundamental_solution_to_pell_equation(d: int) -> Tuple[int, int]:
    """
    Find the minimal solution to Pell's equation x² - Dy² = 1 using continued fractions.

    This function implements Lagrange's algorithm for finding the minimal solution to Pell's equation
    by computing the continued fraction representation of √D. The fundamental solution is found
    from a specific convergent of this continued fraction, determined by the period length.

    Mathematical Background:
    - For any non-square D, √D can be represented as a periodic continued fraction [a₀; a₁, a₂, ..., aₙ]
    - The fundamental solution to x² - Dy² = 1 corresponds to a specific convergent in this expansion
    - If the period length is odd, we need the (2k-1)th convergent where k is the period length
    - If the period length is even, we need the kth convergent
    - For perfect squares, only the trivial solution (1,0) exists

    Algorithm Details:
    1. Check if D is a perfect square - if so, return the trivial solution (1,0)
    2. Compute the continued fraction representation of √D using the standard algorithm:
       - Track the state using values (m, n) in the form (√D + m)/n
       - Generate terms until we detect a cycle (when we reach 2*a₀)
    3. Determine the appropriate convergent based on the period length
    4. Return the integers x and y that satisfy x² - Dy² = 1

    Args:
        d: The coefficient D in Pell's equation

    Returns:
        A tuple of integers (x, y) representing the fundamental solution to x² - Dy² = 1
        For perfect squares, returns the trivial solution (1,0)

    References:
        - https://en.wikipedia.org/wiki/Pell%27s_equation#Continued_fraction_solution
    """
    # Check if d is a perfect square - these have no non-trivial solutions
    if (sqrt_d := sqrt(d)).is_integer():
        return 1, 0  # return the trivial solution x=1, y=0; there are no non-trivial solutions

    # Calculate continued fraction representation of √d
    continued_fraction: Tuple[int, ...] = (floor(sqrt_d),)
    m: int = 0
    n: int = 1
    while continued_fraction[-1] != 2 * continued_fraction[0]:
        m = n * continued_fraction[-1] - m
        n = (d - m * m) // n
        continued_fraction += (floor((sqrt_d + m) / n),)
    if (len_continued_fraction := len(continued_fraction)) % 2 == 0:  # period odd
        return compute_nth_convergent(continued_fraction, 2 * len_continued_fraction - 3).as_integer_ratio()
    else:  # period even
        return compute_nth_convergent(continued_fraction, len_continued_fraction - 2).as_integer_ratio()


test_cases: list[TestCase] = [
    TestCase(
        answer=5,
        is_main_case=False,
        kwargs={'max_d': 7},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=661,
        is_main_case=False,
        kwargs={'max_d': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=9949,
        is_main_case=False,
        kwargs={'max_d': 10000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #66
@register_solution(problem_number=66, test_cases=test_cases)
def diophantine_equation(*, max_d: int) -> int:
    """
    Find the value of D ≤ max_d that produces the largest x value in the minimal solution of x² - Dy² = 1.

    This function solves a special case of Pell's equation (x² - Dy² = 1) by finding the minimal solution
    for each valid value of D up to max_d, then identifying which D produces the largest x value.

    Mathematical Background:
    - Pell's equation is a famous Diophantine equation with applications in number theory
    - For non-square D, the minimal solution can be efficiently found using continued fractions
    - The minimal solution corresponds to a specific convergent in the continued fraction expansion of √D
    - For perfect squares, Pell's equation has no non-trivial solutions except the trivial (1,0)

    Implementation Details:
    - We filter out perfect squares in the generator expression as they only have the trivial solution (1,0)
    - For each valid D, we compute the continued fraction of √D and find the specific convergent
      that gives the minimal solution
    - The fundamental solution is returned as a tuple (x, y) of integers
    - We extract the x value (first element of the tuple) for comparison
    - The algorithm efficiently handles large values of D by using the continued fraction method
      rather than brute force checking of potential solutions
    - Once all minimal solutions are found, we return the D value that produced the largest x

    Args:
        max_d: An integer representing the upper bound for D values to check

    Returns:
        The value of D ≤ max_d for which the minimal solution has the largest x value

    Complexity:
        Time: O(max_d * log(max_d)) - we process each number and the continued fraction computation
              is logarithmic in the value of the number
        Space: O(log(max_d)) - storage for the continued fraction sequence of each number

    Example:
        >>> diophantine_equation(max_d=7)
        5  # x=9 is the largest minimal solution (9² - 5×4² = 1)
        >>> diophantine_equation(max_d=1000)
        661  # This D value produces the largest x among all D ≤ 1000
    """
    return max(((find_fundamental_solution_to_pell_equation(d)[0], d)
                for d in range(2, max_d + 1) if (sqrt(d).is_integer() is False)), key=itemgetter(0))[-1]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(66))
