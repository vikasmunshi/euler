#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 9: Special Pythagorean Triplet [Level 0]. """
from __future__ import annotations

from sys import argv, stderr
from time import perf_counter
from typing import Any


def solve(*, sum_sides: int) -> int:
    try:
        return next(
            (
                a * b * c
                for a in range(1, sum_sides // 4 + 1)
                for b in range(a, sum_sides // 2)
                for c in (sum_sides - a - b,)
                if a**2 + b**2 == c**2
            )
        )
    except StopIteration:
        raise ValueError(f"No Pythagorean triplet exists with sum {sum_sides}")


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
    raise SystemExit(main(sum_sides=int(argv[1])))
