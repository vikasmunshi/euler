#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# solution to Project Euler problem 39
# https://projecteuler.net/problem=39
# Answer: 840
# Notes: 
import textwrap
from collections import Counter
from math import gcd
from typing import cast

from euler.types import ProblemArgs, ProblemArgsList, SolutionProtocol

problem_args_list: ProblemArgsList = [
    ProblemArgs(
        kwargs={'max_perimeter': 10 ** 2},
        answer=60,
    ),
    ProblemArgs(
        kwargs={'max_perimeter': 10 ** 3},
        answer=840,
    ),
    ProblemArgs(
        kwargs={'max_perimeter': 10 ** 4},
        answer=5040,
    ),
    ProblemArgs(
        kwargs={'max_perimeter': 10 ** 5},
        answer=55440,
    ),
    ProblemArgs(
        kwargs={'max_perimeter': 10 ** 6},
        answer=720720,
    ),
]


def integer_right_triangles(*, max_perimeter: int) -> int:
    """
    Find the perimeter value with the maximum number of right-angled triangle solutions.

    This function generates pythagorean triples using Euclid's formula where:
    a = m² - n², b = 2mn, c = m² + n²
    and perimeter p = a + b + c = 2m(m+n)

    Parameters:
        max_perimeter: The maximum perimeter to consider (inclusive)

    Returns:
        The perimeter value with the most integer-sided right triangle solutions

    Algorithm:
    1. Generate primitive pythagorean triples using Euclid's formula with constraints:
       - m > n > 0
       - m and n are coprime (gcd(m,n) = 1)
       - either m or n is even (ensured by incrementing m by 2)
    2. Calculate perimeters of primitive and non-primitive triples
    3. Count the occurrences of each perimeter
    4. Return the perimeter with the highest count
    """
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter ** 0.5) - 6) // 8, 1):
        for m in (m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if gcd(m, n) == 1):
            triangle_perimeters.append(perimeter := 2 * m * (m + n))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return Counter(triangle_perimeters).most_common()[0][0]


solution = cast(SolutionProtocol, integer_right_triangles)

solution.__doc__ = textwrap.dedent(r'''
solution to Project Euler problem 39
https://projecteuler.net/problem=39
If p is the perimeter of a right angle triangle with integral length sides, {a, b, c}, 
there are exactly three solutions for p = 120.
{20,48,52}, {24,45,51}, {30,40,50}
For which value of p <= 1000, is the number of solutions maximised?

    Algorithm:
    1. Generate primitive pythagorean triples using Euclid's formula with constraints:
       - m > n > 0
       - m and n are coprime (gcd(m,n) = 1)
       - either m or n is even (ensured by incrementing m by 2)
    2. Calculate perimeters of primitive and non-primitive triples
    3. Count the occurrences of each perimeter
    4. Return the perimeter with the highest count
''').strip()

if __name__ == '__main__':
    # When run directly, evaluate the solution with test cases
    # Import required modules for evaluating the solution
    from euler.evaluator import evaluate_solution
    from euler.cli import parser
    from euler.logger import logger

    # Parse command-line arguments
    args = parser.parse_args()

    # Set the logging level based on command-line arguments
    logger.setLevel(args.log_level)

    # Extract timeout and maximum worker threads from arguments
    timeout, max_workers = args.timeout, args.max_workers

    # Run the solution with the specified test cases and parameters
    # This validates that our implementation gives the correct answers
    evaluate_solution(solution=solution, args_list=problem_args_list, timeout=timeout, max_workers=max_workers)
