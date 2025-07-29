#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r""" Solution to Project Euler problem 88: product_sum_numbers

Problem Statement:
  A natural number, N, that can be written as the sum and product of a given set
  of at least two natural numbers, \{a_1, a_2, ..., a_k\} is called a product-sum
  number: N = a_1 + a_2 + \cdots + a_k = a_1 * a_2 * \cdots * a_k. For example, 6
  = 1 + 2 + 3 = 1 * 2 * 3. For a given set of size, k, we shall call the smallest
  N with this property a minimal product-sum number. The minimal product-sum
  numbers for sets of size, k = 2, 3, 4, 5, and 6 are as follows.  k=2: 4 = 2 * 2
  = 2 + 2 k=3: 6 = 1 * 2 * 3 = 1 + 2 + 3 k=4: 8 = 1 * 1 * 2 * 4 = 1 + 1 + 2 + 4
  k=5: 8 = 1 * 1 * 2 * 2 * 2 = 1 + 1 + 2 + 2 + 2k=6: 12 = 1 * 1 * 1 * 1 * 2 * 6 =
  1 + 1 + 1 + 1 + 2 + 6 Hence for 2 \le k \le 6, the sum of all the minimal
  product-sum numbers is 4+6+8+12 = 30; note that 8 is only counted once in the
  sum. In fact, as the complete set of minimal product-sum numbers for 2 \le k \le
  12 is \{4, 6, 8, 12, 15, 16\}, the sum is 61. What is the sum of all the minimal
  product-sum numbers for 2 \le k \le 12000?

Solution Approach:
  Document the mathematical approach here.

URL: https://projecteuler.net/problem=88
Answer: None
"""
from __future__ import annotations

from typing import List

from euler.evaluator import evaluate_solutions, register_solution, show_solution
from euler.setup import TestCase

test_cases: list[TestCase] = [
    TestCase(
        answer=30,
        is_main_case=False,
        kwargs={'max_k': 6, 'min_k': 2},
        solution_execution_time=None,
        solved=False
    ),
    TestCase(
        answer=7587457,
        is_main_case=False,
        kwargs={'max_k': 12000, 'min_k': 2},
        solution_execution_time=None,
        solved=False
    ),
]


# Register this function as a solution for problem #88
@register_solution(problem_number=88, test_cases=test_cases)
def product_sum_numbers(*, max_k: int, min_k: int) -> int:
    """
    Calculate the sum of all minimal product-sum numbers for the range min_k ≤ k ≤ max_k.

    A product-sum number is a number that can be expressed as both the sum and product
    of the same set of at least two natural numbers. The minimal product-sum number
    for a given k is the smallest such number that can be expressed using exactly k numbers.

    Args:
        min_k: The minimum set size to consider
        max_k: The maximum set size to consider

    Returns:
        The sum of all unique minimal product-sum numbers in the specified range
    """
    max_k += 1
    min_prod: List[int] = [2 * max_k] * max_k

    def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
        """
        Recursive function to find minimal product-sum numbers.

        This function explores different combinations of numbers to find valid
        product-sum numbers and updates the minimal value for each k.

        Args:
            prod: Current product of the numbers in the set
            total: Current sum of the numbers in the set
            count: Current number of elements in the set
            start: Minimum value to consider for next element (prevents duplicates)
        """
        k = prod - total + count  # Calculate k for the current combination
        if k < max_k:
            min_prod[k] = min(min_prod[k], prod)  # Update minimum for this k if lower
            for i in range(start, (max_k // prod) * 2 + 1):
                find_product_sum(prod * i, total + i, count + 1, i)

    find_product_sum(1, 1, 1, min_k)
    if show_solution():
        print(min_prod[2:])
    return sum(set(min_prod[2:]))


if __name__ == '__main__':
    # Run solution tests and exit with success (0) or failure (>0) status code
    raise SystemExit(evaluate_solutions(88))
