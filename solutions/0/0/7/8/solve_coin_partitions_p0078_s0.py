#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0078/p0078.py
  func: solve_coin_partitions_p0078_s0
"""

from __future__ import annotations

from functools import lru_cache
from itertools import count
from sys import argv


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


def main() -> int:
    print(solve(divisor=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
