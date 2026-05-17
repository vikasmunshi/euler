#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 76: Counting Summations [Level 3]. """
from __future__ import annotations

import functools
from sys import argv, stderr
from time import perf_counter
from typing import Any


@functools.lru_cache(maxsize=None)
def get_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
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


def solve(*, num: int) -> int:
    return len(get_partitions_simple_recursion(number=num, slots=num)) - 1


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
    raise SystemExit(main(num=int(argv[1])))
