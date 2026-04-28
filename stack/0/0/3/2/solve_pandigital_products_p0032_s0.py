#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0032/p0032.py :: solve_pandigital_products_p0032_s0.

Project Euler Problem 32: Pandigital Products.

Problem Statement:
    We shall say that an n-digit number is pandigital if it makes use of all the
    digits 1 to n exactly once; for example, the 5-digit number, 15234, is 1
    through 5 pandigital.

    The product 7254 is unusual, as the identity, 39 × 186 = 7254, containing
    multiplicand, multiplier, and product is 1 through 9 pandigital.

    Find the sum of all products whose multiplicand/multiplier/product identity
    can be written as a 1 through 9 pandigital.

    HINT: Some products can be obtained in more than one way so be sure to only
    include it once in your sum.

Solution Approach:
    Use combinatorics and digit-based checks to verify pandigital conditions.
    Generate multiplicand and multiplier candidates with appropriate digit lengths
    to keep total digits (multiplicand, multiplier, product) equal to 9.
    Use sets to avoid duplicate products.
    Expected complexity is moderate due to search space pruning and digit checks.

Answer: 45228
URL: https://projecteuler.net/problem=32"""
from __future__ import annotations

from itertools import permutations

nine_digits: tuple[str, ...] = ('1', '2', '3', '4', '5', '6', '7', '8', '9')

set_nine_digits: set[str] = set(nine_digits)


def is_nine_pandigital(n: int | str) -> bool:
    return len(str(n)) == 9 and set(str(n)) == set_nine_digits


def solve() -> int:
    return sum(set((c for a_len, b_len in ((1, 4), (2, 3)) for a in permutations(nine_digits, a_len) for b in
                    permutations((d for d in nine_digits if d not in a), b_len) if is_nine_pandigital(
        (a_str := ''.join(a)) + (b_str := ''.join(b)) + str((c := (int(a_str) * int(b_str))))))))


if __name__ == '__main__':
    print(solve())
