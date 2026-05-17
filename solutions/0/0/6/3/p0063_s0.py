#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 63: Powerful Digit Counts [Level 2]. """
from __future__ import annotations

import math
import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any


def n_digit_nth_powers(n: int) -> tuple[int, ...]:
    start_range: int = math.ceil((10 ** (n - 1)) ** (1 / n))
    stop_range: int = math.ceil((10**n - 1) ** (1 / n)) + 1
    return tuple((r for i in range(start_range, stop_range) if len(str((r := (i**n)))) == n))


def solve() -> int:
    result: int = 0
    n: int = 1
    while solutions := n_digit_nth_powers(n):
        result += len(solutions)
        n += 1
        if sys.argv[-1] == "--show":
            print(f"n={n!r} len(solutions)={len(solutions)!r} solutions={solutions!r} ")
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
    raise SystemExit(main())
