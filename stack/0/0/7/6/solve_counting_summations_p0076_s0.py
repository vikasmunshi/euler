#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0076/p0076.py :: solve_counting_summations_p0076_s0.

Project Euler Problem 76: Counting Summations.

Problem Statement:
    It is possible to write five as a sum in exactly six different ways:
    4 + 1
    3 + 2
    3 + 1 + 1
    2 + 2 + 1
    2 + 1 + 1 + 1
    1 + 1 + 1 + 1 + 1

    How many different ways can one hundred be written as a sum of at least
    two positive integers?

Solution Approach:
    Use number theory and combinatorics related to integer partitions.
    Employ dynamic programming to count partitions efficiently.
    Utilize the generating function or recurrence relations for partitions.
    Expected time complexity is O(n²) with n=100 feasible in Python.

Answer: 190569291
URL: https://projecteuler.net/problem=76"""
from __future__ import annotations

from functools import lru_cache
from itertools import count


@lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2


@lru_cache(maxsize=None)
def num_partitions_recursive_pentagonal(number: int) -> int:
    if number <= 0:
        result = int(number == 0)
        return result
    result = 0
    for n in count(1):
        p_1 = num_partitions_recursive_pentagonal(number - pentagonal(n))
        p_2 = num_partitions_recursive_pentagonal(number - pentagonal(-n))
        result += (-1, +1)[n % 2] * (p_1 + p_2)
        if p_1 == 0 and p_2 == 0:
            break
    return result


def solve(*, num: int) -> int:
    result: int = num_partitions_recursive_pentagonal(number=num) - 1
    return result


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(10 ** 6)
    print(solve(num=int(sys.argv[1])))
