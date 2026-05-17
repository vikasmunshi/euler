#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 93: Arithmetic Expressions [Level 8]. """
from __future__ import annotations

import functools
import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any


@functools.lru_cache(maxsize=None)
def eval_all_operations(vals: tuple[int | float, ...]) -> set[int | float]:
    if (len_v := len(vals)) == 1:
        return {vals[0]}
    s = set()
    for i in range(len_v - 1):
        for j in range(i + 1, len_v):
            a, b = (vals[i], vals[j])
            r = tuple([vals[k] for k in range(len_v) if k not in (i, j)])
            s |= eval_all_operations(r + (a + b,))
            s |= eval_all_operations(r + (abs(a - b),))
            s |= eval_all_operations(r + (a * b,))
            if b > 0:
                s |= eval_all_operations(r + (a / b,))
            if a > 0:
                s |= eval_all_operations(r + (b / a,))
    return s


def solve() -> str:
    max_digits: str = ""
    max_length: int = 0
    max_results: set[int] = set()
    for a in range(1, 7):
        for b in range(a + 1, 8):
            for c in range(b + 1, 9):
                for d in range(c + 1, 10):
                    results: set[int] = {int(x) for x in eval_all_operations((a, b, c, d)) if x.is_integer()}
                    length = 0
                    while length + 1 in results:
                        length += 1
                    if length > max_length:
                        max_length, max_digits, max_results = (length, f"{a}{b}{c}{d}", results)
    if sys.argv[-1] == "--show":
        print(f"max_digits={max_digits!r} max_length={max_length!r} max_results={max_results!r}")
    return max_digits


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
