#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 9: special_pythagorean_triplet

Problem Statement:
  A Pythagorean triplet is a set of three natural numbers, a \lt b \lt c, for
  which, a^2 + b^2 = c^2. For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2. There exists
  exactly one Pythagorean triplet for which a + b + c = 1000.Find the product abc.

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=9
Answer: None
"""
from __future__ import annotations

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=60,
        is_main_case=False,
        kwargs={'sum_sides': 12},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=31875000,
        is_main_case=False,
        kwargs={'sum_sides': 1000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #9
@register_solution(problem_number=9, test_cases=test_cases)
def special_pythagorean_triplet(*, sum_sides: int) -> int:
    """
    Find the product of the Pythagorean triplet (a,b,c) with sum equal to sum_sides.

    A Pythagorean triplet is a set of three natural numbers (a < b < c) such that
    a² + b² = c². This function finds a triplet where a + b + c = sum_sides and
    returns their product (a*b*c).

    Args:
        sum_sides: The required sum of the three sides (a + b + c)

    Returns:
        int: The product a*b*c of the Pythagorean triplet
        None: If no Pythagorean triplet exists with the given sum

    Algorithm:
        1. Iterate through possible values of 'a' (optimized range)
        2. For each 'a', iterate through possible values of 'b' (optimized range)
        3. Calculate 'c' as sum_sides - a - b
        4. Check if a² + b² = c² (Pythagorean condition)
        5. Return the product a*b*c for the first triplet found

    Optimization notes:
        - 'a' must be less than sum_sides/4 due to constraints
        - 'b' must be at least 'a' and less than sum_sides/2
        - Using generator expression with next() for efficiency
    """
    try:
        return next(a * b * c
                    for a in range(1, sum_sides // 4 + 1)  # Optimized range for 'a'
                    for b in range(a, sum_sides // 2)  # Optimized range for 'b'
                    for c in (sum_sides - a - b,)  # Calculate 'c' directly
                    if a ** 2 + b ** 2 == c ** 2)  # Pythagorean condition
    except StopIteration:
        raise ValueError(f'No Pythagorean triplet exists with sum {sum_sides}')


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(9))
