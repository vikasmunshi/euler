#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 91: Right Triangles with Integer Coordinates [Level 6]. """
from __future__ import annotations

import math
from sys import argv, stderr
from time import perf_counter
from typing import Any


def solve(*, coordinate_limit: int) -> int:
    triangles_at_p_or_q = sum(
        (
            min(x * m // y, m * (coordinate_limit - y) // x)
            for x in range(1, coordinate_limit + 1)
            for y in range(1, coordinate_limit)
            for m in [math.gcd(x, y)]
        )
    )
    triangles_at_p_or_q *= 2
    triangles_at_origin = 3 * coordinate_limit**2
    return triangles_at_p_or_q + triangles_at_origin


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
    raise SystemExit(main(coordinate_limit=int(argv[1])))
