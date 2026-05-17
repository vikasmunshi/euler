#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 85: Counting Rectangles [Level 2]. """
from __future__ import annotations

import functools
import itertools
import sys
import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any


def num_rectangles(height: int, width: int) -> int:
    return sum(((height - h + 1) * (width - w + 1) for w in range(1, width + 1) for h in range(1, height + 1)))


def delta_func(kv: tuple[int, typing.Any], *, target_num: int) -> int:
    return abs(kv[0] - target_num)


def solve(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
    delta = functools.partial(delta_func, target_num=target_num_rectangles)
    results: dict[int, tuple[int, int, int]] = {}
    for height, width in itertools.product(range(2, max_side), repeat=2):
        results[(num := num_rectangles(height, width))] = (height, width, height * width)
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
