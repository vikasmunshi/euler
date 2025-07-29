#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 26: reciprocal_cycles

Problem Statement:
  A unit fraction contains 1 in the numerator. The decimal representation of the
  unit fractions with denominators 2 to 10 are given: \begin{align} 1/2 &= 0.5\\
  1/3 &=0.(3)\\ 1/4 &=0.25\\ 1/5 &= 0.2\\ 1/6 &= 0.1(6)\\ 1/7 &= 0.(142857)\\ 1/8
  &= 0.125\\ 1/9 &= 0.(1)\\ 1/10 &= 0.1 \end{align} Where 0.1(6) means
  0.166666\cdots, and has a 1-digit recurring cycle. It can be seen that 1/7 has a
  6-digit recurring cycle. Find the value of d \lt 1000 for which 1/d contains the
  longest recurring cycle in its decimal fraction part.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=26
Answer: None
"""
from __future__ import annotations

from math import gcd
from typing import Optional

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=7,
        is_main_case=False,
        kwargs={'max_val': 10},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=97,
        is_main_case=False,
        kwargs={'max_val': 100},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=983,
        is_main_case=False,
        kwargs={'max_val': 1000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=9967,
        is_main_case=False,
        kwargs={'max_val': 10000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #26
@register_solution(problem_number=26, test_cases=test_cases)
def reciprocal_cycles(*, max_val: int) -> int:
    """
    Find the value of d < max_val with the longest recurring decimal cycle in 1/d.

    This solution uses number theory to efficiently find the denominator with the longest
    recurring cycle. It leverages the fact that for a fraction 1/d, the length of its recurring
    decimal cycle equals the multiplicative order of 10 modulo d (when gcd(10, d) = 1).

    Args:
        max_val: The upper bound for d (exclusive)

    Returns:
        The value of d < max_val for which 1/d has the longest recurring decimal cycle

    Example:
        >>> reciprocal_cycles(max_val=10)
        7  # 1/7 has a 6-digit recurring cycle: 0.(142857)
        >>> reciprocal_cycles(max_val=1000)
        983  # 1/983 has a 982-digit recurring cycle
    """
    # Using walrus operator ":=" to assign and test d in a single expression
    # Starting from max_val and checking in descending order (more efficient)
    # Only considering values where gcd(d, 10) = 1 (not divisible by 2 or 5)
    return max((multiplicative_order(a=10, modulus=d), d)
               for i in range(max(max_val // 10, 10))
               if (d := max_val - i) > 6 and gcd(d, 10) == 1)[1]


def multiplicative_order(a: int, modulus: int) -> Optional[int]:
    """
    Calculate the multiplicative order of a modulo modulus.

    The multiplicative order is the smallest positive integer k such that a^k ≡ 1 (mod modulus).
    For decimal fractions 1/d, the length of the recurring cycle equals the multiplicative
    order of 10 modulo d (when gcd(10, d) = 1).

    Args:
        a: The base number (for decimal fractions, this is 10)
        modulus: The modulus to calculate against (the denominator d)

    Returns:
        The multiplicative order if it exists within modulus iterations, None otherwise
    """
    r = 1
    for k in range(1, modulus):
        r = (r * a) % modulus
        if r == 1:
            return k
    else:
        return None


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(26))
