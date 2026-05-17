#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 78: Coin Partitions [Level 3]. """
from __future__ import annotations

import functools
import itertools
from sys import argv, stderr
from time import perf_counter
from typing import Any


@functools.lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2


def least_number_with_partitions_divisible_by(divisor: int) -> int:
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


def solve(*, divisor: int) -> int:
    return least_number_with_partitions_divisible_by(divisor=divisor)


def main(**kwargs: Any) -> int:
    """
    Usage: ./file.py <kwarg>... [--runs=1] [--show]
    Output: "<runs> <avg_seconds> <result>"
    """
    try:
        runs_arg: str = next((arg for arg in argv[1:] if arg.startswith("--runs=")))
        runs: int = int(runs_arg.split("=", 1)[1])
        assert runs > 0
    except (AssertionError, StopIteration, ValueError):
        runs = 1
    elapsed: list[float] = []
    result: int | None = None
    rc: int = 0
    errors: list[str] = []
    for _ in range(runs):
        _start, _result, _stop = (perf_counter(), solve(**kwargs), perf_counter())
        elapsed.append(_stop - _start)
        if result is not None and _result != result:
            errors.append(f"Expected consistent result, got {_result} previous result={result}")
        result = _result
    if result is None:
        errors.append("Expected a result, got None")
    average: float = sum(elapsed) / len(elapsed)
    if errors:
        print("\n".join(errors), file=stderr)
        rc = 1
    print(f"{runs} {average} {result}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(divisor=int(argv[1])))
