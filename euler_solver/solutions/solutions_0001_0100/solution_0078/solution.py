#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
URL: https://projecteuler.net/problem=78
"""
from __future__ import annotations

from functools import lru_cache
from itertools import count
from typing import Any

from euler_solver.c_libs import use_wrapped_c_function
from euler_solver.logger import logger
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 78
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'preliminary', 'input': {'divisor': 1_000}},
    {'category': 'main', 'input': {'divisor': 1_000_000}}
]


@lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2  # pentagonal number formula


@use_wrapped_c_function('p0078')
def least_number_with_partitions_divisible_by(divisor: int) -> int:
    partitions = [1]  # Initialize with p(0) = 1

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

    return -1  # Failsafe for unexpected cases


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_coin_partitions_p0078_s0(*, divisor: int) -> int:
    return least_number_with_partitions_divisible_by(divisor=divisor)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
