#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 76: Counting Summations [Level 3]. """
from __future__ import annotations

import functools
import sys

from solver.runners import runner


@functools.lru_cache(maxsize=None)
def num_partitions_simple_recursion(*, number: int, slots: int) -> int:
    """Count partitions of number with largest part <= slots; min(.) keeps parts non-increasing."""
    if number < 0 or slots < 0:
        raise ValueError("number and slots must be non-negative")
    if number < slots:
        raise ValueError("number must be greater than or equal to slots")
    if number <= 1:
        return number
    return sum(
        (num_partitions_simple_recursion(number=number - n, slots=min(number - n, n)) for n in range(1, slots + 1))
    ) + (1 if number <= slots else 0)


@runner.main
def solve(*args: str) -> str:
    """Memoized 2D partition recurrence count(num, num) minus the trivial partition; O(n^3)."""
    num = runner.parse_int(args[0])
    sys.setrecursionlimit(10 ** 6)

    return str(num_partitions_simple_recursion(number=num, slots=num) - 1)


if __name__ == "__main__":
    raise SystemExit(solve())
