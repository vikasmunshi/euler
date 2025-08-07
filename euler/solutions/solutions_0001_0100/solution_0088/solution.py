#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 88: Product Sum Numbers.

  Problem Statement:
    A natural number, N, that can be written as the sum and product of a given
    set of at least two natural numbers, {a_1, a_2, ..., a_k} is called a
    product-sum number: N = a_1 + a_2 + ... + a_k = a_1 x a_2 x ... x a_k.

    For example, 6 = 1 + 2 + 3 = 1 x 2 x 3.

    For a given set of size, k, we shall call the smallest N with this property
    a minimal product-sum number. The minimal product-sum numbers for sets of
    size, k = 2, 3, 4, 5, and 6 are as follows.

    k=2: 4 = 2 x 2 = 2 + 2
    k=3: 6 = 1 x 2 x 3 = 1 + 2 + 3
    k=4: 8 = 1 x 1 x 2 x 4 = 1 + 1 + 2 + 4
    k=5: 8 = 1 x 1 x 2 x 2 x 2 = 1 + 1 + 2 + 2 + 2
    k=6: 12 = 1 x 1 x 1 x 1 x 2 x 6 = 1 + 1 + 1 + 1 + 2 + 6

    Hence for 2 <= k <= 6, the sum of all the minimal product-sum numbers is
    4+6+8+12 = 30; note that 8 is only counted once in the sum.

    In fact, as the complete set of minimal product-sum numbers for 2 <= k <= 12
    is {4, 6, 8, 12, 15, 16}, the sum is 61.

    What is the sum of all the minimal product-sum numbers for 2 <= k <= 12000?

  Solution Approach:
    To approach this problem, consider the properties of numbers that are both
    the sum and product of a set of natural numbers. You will need to generate
    all possible combinations of factors for sets of various sizes, tracking
    those whose sum equals the product.

    Efficiently searching for minimal product-sum numbers involves understanding
    factorization, partitioning numbers into their additive and multiplicative
    components, and avoiding redundant calculations. Implementing a recursive
    backtracking algorithm with pruning strategies can help explore valid sets.

    Additionally, keep track of minimal values found for each set size k to
    compute the final sum efficiently without duplicates. Using combinatorial
    optimizations and memoization will significantly reduce the search space.

  Test Cases:
    preliminary:
      max_k=6,
      min_k=2,
      answer=30.

    main:
      max_k=12000,
      min_k=2,
      answer=7587457.


  Answer: 7587457
  URL: https://projecteuler.net/problem=88
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution, show_solution


@register_solution(euler_problem=88, test_case_category=TestCaseCategory.EXTENDED)
def product_sum_numbers(*, max_k: int, min_k: int) -> int:
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
        k = prod - total + count
        if k < max_k:
            min_prod[k] = min(min_prod[k], prod)
            for i in range(start, max_k // prod * 2 + 1):
                find_product_sum(prod * i, total + i, count + 1, i)

    find_product_sum(1, 1, 1, min_k)
    if show_solution():
        print(min_prod[2:])
    return sum(set(min_prod[2:]))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=88, time_out_in_seconds=300, mode='evaluate'))
