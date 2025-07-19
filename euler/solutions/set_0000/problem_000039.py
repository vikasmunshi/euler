#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solution to Project Euler problem 39: Integer right triangles

Problem Statement:
If p is the perimeter of a right angle triangle with integral length sides, {a, b, c},
there are exactly three solutions for p = 120.
{20,48,52}, {24,45,51}, {30,40,50}

For which value of p ≤ 1000, is the number of solutions maximised?

Solution Approach:
This implementation uses Euclid's formula to efficiently generate Pythagorean triples and count
the number of right triangles with integer sides for each perimeter value. By applying the formula
to generate primitive triples and their multiples, we can identify which perimeter value has the
most possible triangle configurations.

The formula used is:
a = m² - n², b = 2mn, c = m² + n², where perimeter p = a + b + c = 2m(m+n)
with constraints: m > n > 0, gcd(m,n) = 1, and one of m or n is even.

Test Cases:
- For max_perimeter=100, the answer is 60 (with 2 solutions)
- For max_perimeter=1000, the answer is 840 (with 8 solutions)
- For max_perimeter=10000, the answer is 5040 (with 32 solutions)

URL: https://projecteuler.net/problem=39
Answer: 840
"""

from collections import Counter
from math import gcd

from euler.evaluator import evaluate_solutions, register_solution
from euler.types import ProblemArgs, ProblemArgsList

# The problem number from Project Euler (https://projecteuler.net/problem=39)
problem_number: int = 39

problem_args_list: ProblemArgsList = [
    ProblemArgs(kwargs={'max_perimeter': 10 ** 2}, answer=60, ),
    ProblemArgs(kwargs={'max_perimeter': 10 ** 3}, answer=840, ),
    ProblemArgs(kwargs={'max_perimeter': 10 ** 4}, answer=5040, ),
    ProblemArgs(kwargs={'max_perimeter': 10 ** 5}, answer=55440, ),
    ProblemArgs(kwargs={'max_perimeter': 10 ** 6}, answer=720720, ),
]


@register_solution(problem_number=problem_number, args_list=problem_args_list)
def integer_right_triangles(*, max_perimeter: int) -> int:
    """
    Find the perimeter value that maximizes the number of integer right triangles.

    This solution uses Euclid's formula to generate Pythagorean triples, where
    for coprime integers m > n > 0 with one even and one odd:
    a = m² - n², b = 2mn, c = m² + n²
    and perimeter p = a + b + c = 2m(m+n)

    We generate all primitive Pythagorean triples within the perimeter limit and
    their non-primitive multiples, then find which perimeter value has the most
    different triangle solutions.

    Args:
        max_perimeter: The maximum perimeter to consider (inclusive)

    Returns:
        The perimeter value with the most integer-sided right triangle solutions

    Examples:
        >>> integer_right_triangles(max_perimeter=120)
        120  # Has 3 solutions: {20,48,52}, {24,45,51}, {30,40,50}
        >>> integer_right_triangles(max_perimeter=1000)
        840  # Has 8 different triangle solutions
    """
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter ** 0.5) - 6) // 8, 1):
        for m in (m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if gcd(m, n) == 1):
            triangle_perimeters.append(perimeter := 2 * m * (m + n))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return Counter(triangle_perimeters).most_common()[0][0]


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(problem_number))
