#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0076/p0076.py :: solve_counting_summations_p0076_s2.

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
def get_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
    if safe_limit and number > safe_limit:
        raise OverflowError(f'number must be less than safe_limit={safe_limit!r}')
    if number < 0 or slots < 0:
        raise ValueError('number and slots must be non-negative')
    if number < slots:
        raise ValueError('number must be greater than or equal to slots')
    if number <= 1:
        return [] if number == 0 else [[1]]
    partitions: list[list[int]] = []
    for n in range(1, slots + 1):
        if n == number:
            partitions.append([n])
        else:
            for partition in get_partitions_simple_recursion(number=number - n, slots=min(number - n, n),
                                                             safe_limit=safe_limit):
                partitions.append([n] + partition)
    for partition in partitions:
        assert sum(partition) == number, f'partition={partition!r} sum(partition)={sum(partition)!r} number={number!r}'
    return partitions


def solve(*, num: int) -> int:
    return len(get_partitions_simple_recursion(number=num, slots=num)) - 1


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(10 ** 6)
    print(solve(num=int(sys.argv[1])))
