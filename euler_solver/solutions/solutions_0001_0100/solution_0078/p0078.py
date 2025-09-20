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

from ctypes import c_int
from functools import lru_cache
from itertools import count
from sys import maxsize
from typing import Any, Callable

from euler_solver.framework import evaluate, import_c_lib, logger, register_solution, use_c_function

euler_problem: int = 78
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'dev', 'input': {'divisor': 1000}, 'answer': 449},
    {'category': 'main', 'input': {'divisor': 1000000}, 'answer': 55374},
]


@lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2  # pentagonal number formula


def c_wrapper() -> tuple[Callable, ...]:
    # Import the C library and function
    c_lib = import_c_lib(euler_problem)

    _c_least_n = getattr(c_lib, 'least_number_with_partitions_divisible_by')
    _c_least_n.argtypes = [c_int]
    _c_least_n.restype = c_int

    def least_number_with_partitions_divisible_by_c(divisor: int) -> int:
        """
        Return the least n such that the partition number p(n) is divisible by 'divisor'.

        Parameters:
            divisor (int): Positive modulus (e.g., 1_000_000 for Euler 78)

        Returns:
            int: The least n where p(n) % divisor == 0. Raises ValueError for invalid input.
        """
        if not (isinstance(divisor, int) and 0 < divisor < maxsize):
            raise ValueError(f'divisor must be a positive int less than {maxsize}')
        n = _c_least_n(c_int(divisor))
        if n < 0:
            raise RuntimeError('C computation failed')
        return int(n)

    return (least_number_with_partitions_divisible_by_c,)


@use_c_function(c_wrapper, 0)
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


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_coin_partitions_p0078_s0(*, divisor: int) -> int:
    return least_number_with_partitions_divisible_by(divisor=divisor)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
