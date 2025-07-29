#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 75: singular_integer_right_triangles

Problem Statement:
  It turns out that \pu{12 cm} is the smallest length of wire that can be bent to
  form an integer sided right angle triangle in exactly one way, but there are
  many more examples.  \pu{\mathbf{12} \mathbf{cm}}: (3,4,5) \pu{\mathbf{24}
  \mathbf{cm}}: (6,8,10) \pu{\mathbf{30} \mathbf{cm}}: (5,12,13) \pu{\mathbf{36}
  \mathbf{cm}}: (9,12,15) \pu{\mathbf{40} \mathbf{cm}}: (8,15,17) \pu{\mathbf{48}
  \mathbf{cm}}: (12,16,20) In contrast, some lengths of wire, like \pu{20 cm},
  cannot be bent to form an integer sided right angle triangle, and other lengths
  allow more than one solution to be found; for example, using \pu{120 cm} it is
  possible to form exactly three different integer sided right angle triangles.
  \pu{\mathbf{120} \mathbf{cm}}: (30,40,50), (20,48,52), (24,45,51) Given that L
  is the length of the wire, for how many values of L \le 1\,500\,000 can exactly
  one integer sided right angle triangle be formed?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=75
Answer: None
"""
from __future__ import annotations

from math import gcd
from typing import Dict, Generator

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=6,
        is_main_case=False,
        kwargs={'max_perimeter': 50},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=161667,
        is_main_case=False,
        kwargs={'max_perimeter': 1500000},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=1067080,
        is_main_case=False,
        kwargs={'max_perimeter': 10000000},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #75
@register_solution(problem_number=75, test_cases=test_cases)
def singular_integer_right_triangles(*, max_perimeter: int) -> int:
    """Count perimeter values that form exactly one integer-sided right triangle.

    This function solves Project Euler problem 75 by:
    1. Generating all possible Pythagorean triple perimeters up to max_l
    2. Counting how many times each perimeter value occurs
    3. Counting how many perimeter values occur exactly once

    When a perimeter occurs exactly once, it means there is exactly one way to form
    an integer-sided right triangle with that perimeter.

    Args:
        max_perimeter: Maximum perimeter length to consider (inclusive)

    Returns:
        Number of perimeter values ≤ max_l that form exactly one integer-sided right triangle

    Time Complexity:
        O(max_l * log(max_l))

    Space Complexity:
        O(max_l), as we need to store a counter for each unique perimeter value

    Example:
        >>> singular_integer_right_triangles(max_perimeter=50)
        6  # Perimeters 12, 24, 30, 36, 40, and 48 each form exactly one right triangle
    """
    # Dictionary to track how many times each perimeter occurs
    perimeter_count: Dict[int, int] = {}

    # Generate all Pythagorean triple perimeters up to max_l
    for perimeter in gen_pythagorean_triangle_perimeters(max_perimeter=max_perimeter):
        # Increment the count for this perimeter
        perimeter_count[perimeter] = perimeter_count.get(perimeter, 0) + 1

    # Count how many perimeters occur exactly once
    return sum(count == 1 for count in perimeter_count.values())


def gen_pythagorean_triangle_perimeters(*, max_perimeter: int) -> Generator[int, None, None]:
    """Generate all Pythagorean triple perimeters up to a maximum value.

    This function uses Euclid's formula to generate Pythagorean triples and their perimeters.
    For coprime integers m > n > 0 where one is even and one is odd, the formula generates
    a primitive Pythagorean triple (a, b, c) where:

    a = m² - n²
    b = 2mn
    c = m² + n²

    The perimeter is p = a + b + c = 2m(m + n)

    The function generates both primitive triples and their multiples (non-primitive triples).

    Args:
        max_perimeter: The maximum perimeter value to generate (inclusive)

    Yields:
        Integer perimeter values of right triangles with integer sides, in no particular order

    Time Complexity:
        O(max_perimeter * log(max_perimeter))

    Example:
        >>> list(gen_pythagorean_triangle_perimeters(max_perimeter=50))
        [12, 24, 30, 36, 40, 48, 24, 48, 30, 36, 40, 48]
        # Note: Duplicates appear because different parameter combinations can yield the same perimeter
    """
    # Upper bound for m is derived from the formula p = 2m(m+n) ≤ max_perimeter
    # Since n ≥ 1, p ≥ 2m(m+1) ≥ 2m² + 2m
    # Therefore m ≤ sqrt(max_perimeter/2)
    for m in range(2, int((max_perimeter / 2) ** 0.5)):
        # Ensure m and n have different parity (one even, one odd)
        # If m is even, n starts at 1 and increments by 2 (odd values only)
        # If m is odd, n starts at 2 and increments by 2 (even values only)
        for n in range((m % 2) + 1, m, 2):
            # Skip if m and n have a common factor (not coprime)
            if gcd(m, n) != 1:
                continue

            # Calculate the perimeter of the primitive triple
            # p = 2m(m+n)
            p, k = 2 * m * (m + n), 1

            # Generate all multiples of the primitive triple's perimeter
            # up to the maximum perimeter
            while (perimeter := k * p) <= max_perimeter:
                yield perimeter
                k += 1


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(75))
