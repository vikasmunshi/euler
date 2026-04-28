#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0024/p0024.py :: solve_lexicographic_permutations_p0024_s0.

Project Euler Problem 24: Lexicographic Permutations.

Problem Statement:
    A permutation is an ordered arrangement of objects. For example, 3124 is one
    possible permutation of the digits 1, 2, 3 and 4. If all of the permutations
    are listed numerically or alphabetically, we call it lexicographic order.
    The lexicographic permutations of 0, 1 and 2 are:

    012
    021
    102
    120
    201
    210

    What is the millionth lexicographic permutation of the digits 0, 1, 2, 3, 4, 5,
    6, 7, 8 and 9?

Solution Approach:
    Use combinatorics and factorial number system to directly compute the millionth
    permutation without generating all permutations. Calculate digit positions by
    dividing the rank by factorial values and updating remaining rank and digits.
    This approach is efficient with O(n^2) time complexity for n=10 digits.

Answer: 2783915460
URL: https://projecteuler.net/problem=24"""
from __future__ import annotations

from math import factorial


def recursive_solution(digits: str, permutation_number: int) -> str:
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, factorial(len(digits) - 1))
    result: str = digits[current] + recursive_solution(digits=digits[:current] + digits[current + 1:],
                                                       permutation_number=remaining + 1)
    return result


def solve(*, digits: str, permutation_number: int) -> str:
    return recursive_solution(digits=digits, permutation_number=permutation_number)


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(10 ** 6)
    print(solve(digits=str(sys.argv[1]), permutation_number=int(sys.argv[2])))
