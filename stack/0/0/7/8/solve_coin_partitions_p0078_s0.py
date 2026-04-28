#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0078/p0078.py :: solve_coin_partitions_p0078_s0.

Project Euler Problem 78: Coin Partitions.

Problem Statement:
    Let p(n) represent the number of different ways in which n coins can be separated
    into piles. For example, five coins can be separated into piles in exactly seven
    different ways, so p(5) = 7.

    OOOOO
    OOOO   O
    OOO   OO
    OOO   O   O
    OO   OO   O
    OO   O   O   O
    O   O   O   O   O

    Find the least value of n for which p(n) is divisible by one million.

Solution Approach:
    Use number theory and partition function properties. Implement a dynamic programming
    approach to compute p(n) efficiently using Euler’s pentagonal number theorem.
    Detect the smallest n where p(n) modulo 1,000,000 is zero. The algorithm is typically
    O(n * sqrt(n)) time complexity.

Answer: 55374
URL: https://projecteuler.net/problem=78"""
from __future__ import annotations

from functools import lru_cache
from itertools import count


@lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2


def least_number_with_partitions_divisible_by(divisor: int) -> int:
    partitions = [1]
    for n in count(1):
        partition_value = 0
        k = 1
        while True:
            pent_k1 = pentagonal(k)
            pent_k2 = pentagonal(-k)
            if pent_k1 > n:
                break
            partition_value += (-1) ** (k - 1) * partitions[n - pent_k1]
            if 0 < pent_k2 <= n:
                partition_value += (-1) ** (k - 1) * partitions[n - pent_k2]
            k += 1
        partition_value %= divisor
        partitions.append(partition_value)
        if partition_value == 0:
            return n
    return -1


def solve(*, divisor: int) -> int:
    return least_number_with_partitions_divisible_by(divisor=divisor)


if __name__ == '__main__':
    import sys

    print(solve(divisor=int(sys.argv[1])))
