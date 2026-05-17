#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 44: Pentagon Numbers [Level 2]. """
from __future__ import annotations

import math
from sys import argv, stderr
from time import perf_counter
from typing import Any


def nth_pentagonal_number(n: int) -> int:
    return n * (3 * n - 1) // 2


def is_pentagonal_number(n: int) -> bool:
    return ((1 + math.sqrt(1 + 24 * n)) / 6).is_integer()


def solve() -> int:
    i = 0
    while i := (i + 1):
        p_i = nth_pentagonal_number(i)
        for j in range(i - 1, 0, -1):
            p_j = nth_pentagonal_number(j)
            if is_pentagonal_number(p_i - p_j) and is_pentagonal_number(p_i + p_j):
                return p_i - p_j
    else:
        raise ValueError("No solution found")


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
    raise SystemExit(main())
