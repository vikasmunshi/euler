#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 76: Counting Summations [Level 3]. """
from __future__ import annotations

import functools

from solver.runners import runner


@functools.lru_cache(maxsize=None)
def get_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
    """Materialize all partitions of number with largest part <= slots; safe_limit guards blow-up."""
    if safe_limit and number > safe_limit:
        raise OverflowError(f"number must be less than safe_limit={safe_limit!r}")
    if number < 0 or slots < 0:
        raise ValueError("number and slots must be non-negative")
    if number < slots:
        raise ValueError("number must be greater than or equal to slots")
    if number <= 1:
        return [] if number == 0 else [[1]]
    partitions: list[list[int]] = []
    for n in range(1, slots + 1):
        if n == number:
            partitions.append([n])
        else:
            for partition in get_partitions_simple_recursion(
                number=number - n, slots=min(number - n, n), safe_limit=safe_limit
            ):
                partitions.append([n] + partition)
    for partition in partitions:
        assert sum(partition) == number, f"partition={partition!r} sum(partition)={sum(partition)!r} number={number!r}"
    return partitions


@runner.main
def solve(*args: str) -> str:
    """Explicit partition enumeration; count partitions of num minus 1, raising OverflowError past safe_limit."""
    num = runner.parse_int(args[0])

    return str(len(get_partitions_simple_recursion(number=num, slots=num)) - 1)


if __name__ == "__main__":
    raise SystemExit(solve())
