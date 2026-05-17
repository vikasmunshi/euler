#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 76: Counting Summations [Level 3]. """
from __future__ import annotations

import functools
import itertools
import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any


@functools.lru_cache(maxsize=None)
def pentagonal(x: int) -> int:
    return x * (3 * x - 1) // 2


@functools.lru_cache(maxsize=None)
def num_partitions_recursive_pentagonal(number: int) -> int:
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


def solve(*, num: int) -> int:
    result: int = num_partitions_recursive_pentagonal(number=num) - 1
    return result


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
    sys.setrecursionlimit(10**6)
    raise SystemExit(main(num=int(argv[1])))
