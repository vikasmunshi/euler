#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 85: Counting Rectangles [Level 2]. """
from __future__ import annotations

import bisect
import functools
import sys
import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any


def num_rectangles_along_axis(length: int) -> int:
    return sum((length - num + 1 for num in range(1, length + 1)))


def delta_func(kv: tuple[int, typing.Any], *, target_num: int) -> int:
    return abs(kv[0] - target_num)


def solve(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
    delta = functools.partial(delta_func, target_num=target_num_rectangles)
    results: dict[int, tuple[int, int, int]] = {}
    numbers: tuple[int, ...] = tuple((num_rectangles_along_axis(length) for length in range(1, max_side)))
    len_numbers = len(numbers)
    num: int = 0
    for width, num_width in enumerate(numbers, start=1):
        j = bisect.bisect_left(a=numbers, x=target_num_rectangles // num_width)
        for height in (j + 1, j + 2):
            if 0 <= height - 1 < len_numbers:
                results[(num := (numbers[height - 1] * num_width))] = (height, width, height * width)
        if delta((num, None)) <= max_error:
            break
    if sys.argv[-1] == "--show":
        result = min(results.items(), key=delta)
        print(f"Grid with {result[0]} rectangles: {result[1]}")
    return min(results.items(), key=delta)[1][2]


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
    raise SystemExit(main(max_error=int(argv[1]), max_side=int(argv[2]), target_num_rectangles=int(argv[3])))
