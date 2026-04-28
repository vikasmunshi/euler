#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0076/p0076.py :: solve_counting_summations_p0076_s1.

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


@lru_cache(maxsize=None)
def num_partitions_simple_recursion(*, number: int, slots: int) -> int:
    if number < 0 or slots < 0:
        raise ValueError('number and slots must be non-negative')
    if number < slots:
        raise ValueError('number must be greater than or equal to slots')
    if number <= 1:
        return number
    return sum(
        (num_partitions_simple_recursion(number=number - n, slots=min(number - n, n)) for n in range(1, slots + 1))) + (
        1 if number <= slots else 0)


def solve(*, num: int) -> int:
    return num_partitions_simple_recursion(number=num, slots=num) - 1


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(10 ** 6)
    print(solve(num=int(sys.argv[1])))
