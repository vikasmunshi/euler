#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0088/p0088.py :: solve_product_sum_numbers_p0088_s0.

Project Euler Problem 88: Product-sum Numbers.

Problem Statement:
    A natural number, N, that can be written as the sum and product of a given set of at
    least two natural numbers, {a_1, a_2, ..., a_k} is called a product-sum number:
    N = a_1 + a_2 + ... + a_k = a_1 × a_2 × ... × a_k.

    For example, 6 = 1 + 2 + 3 = 1 × 2 × 3.

    For a given set size k, the smallest N with this property is called a minimal
    product-sum number. The minimal product-sum numbers for k = 2, 3, 4, 5, and 6 are:
        k=2: 4 = 2 × 2 = 2 + 2
        k=3: 6 = 1 × 2 × 3 = 1 + 2 + 3
        k=4: 8 = 1 × 1 × 2 × 4 = 1 + 1 + 2 + 4
        k=5: 8 = 1 × 1 × 2 × 2 × 2 = 1 + 1 + 2 + 2 + 2
        k=6: 12 = 1 × 1 × 1 × 1 × 2 × 6 = 1 + 1 + 1 + 1 + 2 + 6

    The sum of all minimal product-sum numbers for 2 ≤ k ≤ 6 is 4 + 6 + 8 + 12 = 30,
    counting 8 only once.

    For 2 ≤ k ≤ 12, the complete set of minimal product-sum numbers is {4, 6, 8, 12, 15, 16}
    and the sum is 61.

    What is the sum of all the minimal product-sum numbers for 2 ≤ k ≤ 12000?

Solution Approach:
    Use backtracking to generate factor combinations and identify product-sum numbers.
    Keep track of minimal values for each k. Efficiently prune the search space.
    Use number theory and combinatorics to manage factor sets and sums.
    Expected complexity requires careful optimization and caching.

Answer: 7587457
URL: https://projecteuler.net/problem=88"""
from __future__ import annotations

import sys
from typing import List


def show_solution() -> bool:
    return '--show' in sys.argv


def solve(*, max_k: int, min_k: int) -> int:
    max_k += 1
    min_prod: List[int] = [2 * max_k] * max_k

    def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
        k = prod - total + count
        if k < max_k:
            min_prod[k] = min(min_prod[k], prod)
            for i in range(start, max_k // prod * 2 + 1):
                find_product_sum(prod * i, total + i, count + 1, i)

    find_product_sum(1, 1, 1, min_k)
    if show_solution():
        print(min_prod[2:], file=sys.stderr)
    return sum(set(min_prod[2:]))


if __name__ == '__main__':
    sys.setrecursionlimit(10 ** 6)
    print(solve(max_k=int(sys.argv[1]), min_k=int(sys.argv[2])))
