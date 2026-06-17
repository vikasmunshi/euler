#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 76: Counting Summations [Level 3]. """
from __future__ import annotations

import functools
import itertools
import sys

from solver.runners import runner


@functools.lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    """Return the generalized pentagonal number g(x) = x(3x-1)/2."""
    return x * (3 * x - 1) // 2


@functools.lru_cache(maxsize=None)
def num_partitions_recursive_pentagonal(number: int) -> int:
    """Partition count p(number) via Euler's pentagonal recurrence; O(sqrt(n)) terms per value."""
    n: int
    if number <= 0:
        result = int(number == 0)
        return result
    result = 0
    for n in itertools.count(1):
        p_1 = num_partitions_recursive_pentagonal(number - pentagonal(n))
        p_2 = num_partitions_recursive_pentagonal(number - pentagonal(-n))
        result += (-1, +1)[n % 2] * (p_1 + p_2)
        if p_1 == 0 and p_2 == 0:
            break
    return result


@runner.main
def solve(*args: str) -> str:
    """Euler's pentagonal number theorem for p(num), minus 1 for the trivial partition; O(n*sqrt(n))."""
    num = runner.parse_int(args[0])
    sys.setrecursionlimit(10 ** 6)

    result: int = num_partitions_recursive_pentagonal(number=num) - 1
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
