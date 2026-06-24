#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 78: Coin Partitions [Level 3]. """
from __future__ import annotations

import functools
import itertools

from solver.runners import runner


@functools.lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    """Return the generalized pentagonal number g(x) = x(3x-1)/2."""
    return x * (3 * x - 1) // 2


def least_number_with_partitions_divisible_by(divisor: int) -> int:
    """Bottom-up DP for p(n) via Euler's pentagonal recurrence, reduced mod divisor; O(N*sqrt(N)).

    Each n sums (-1)^(k-1) p(n - g(k)) over the (k, -k) pentagonal pairs, stopping once g(k) > n
    (only O(sqrt(n)) terms contribute). The first n with p(n) == 0 (mod divisor) is returned.
    """
    partitions = [1]
    for n in itertools.count(1):
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


@runner.main
def solve(*args: str) -> str:
    """Parse the divisor and return the least n with p(n) divisible by it."""
    divisor = runner.parse_int(args[0])

    return str(least_number_with_partitions_divisible_by(divisor=divisor))


if __name__ == "__main__":
    raise SystemExit(solve())
