#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 15: lattice_paths

Problem Statement:
  Starting in the top left corner of a 2 * 2 grid, and only being able to move to
  the right and down, there are exactly 6 routes to the bottom right corner.   How
  many such routes are there through a 20 * 20 grid?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=15
Answer: None
"""
from __future__ import annotations

from math import factorial

from euler.evaluator import evaluate_solutions, register_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=6,
        is_main_case=False,
        kwargs={'lattice_size': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=137846528820,
        is_main_case=False,
        kwargs={'lattice_size': 20},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #15
@register_solution(problem_number=15, test_cases=test_cases)
def lattice_paths(*, lattice_size: int) -> int:
    """Calculate the number of routes through a square lattice of a given size.

    This function computes the number of unique paths from the top-left corner to the
    bottom-right corner of an n×n grid, where only rightward and downward movements are allowed.

    Mathematical Background:
    The problem reduces to a combination problem from discrete mathematics. For any path:
    - We need exactly n moves to the right and n moves down (total 2n moves)
    - The question becomes: "In how many ways can we choose which n positions out of
      the 2n total will be right-moves?"
    - This is precisely the binomial coefficient C(2n,n) = (2n)!/(n!)²

    Args:
        lattice_size: Size of the square lattice (an n×n grid has n+1 points on each side)

    Returns:
        The number of possible routes from top-left to bottom-right corner

    Implementation Notes:
    - The solution uses Python's factorial function from the math module
    - The formula calculates exactly: (2n)!/(n!)²
    - Integer division (//) is used since the result is guaranteed to be an integer
    - For large values of n, the factorials grow very large, but Python handles
      arbitrary-precision integers automatically

    Examples:
        >>> lattice_paths(lattice_size=1)
        2  # For a 1×1 grid: right-down or down-right
        >>> lattice_paths(lattice_size=2)
        6  # For a 2×2 grid: 6 distinct paths
    """
    return factorial(2 * lattice_size) // (factorial(lattice_size) ** 2)


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(15))
