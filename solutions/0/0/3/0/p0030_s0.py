#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 30: Digit Fifth Powers [Level 0]. """
from __future__ import annotations

import itertools
import math
from sys import argv, stderr
from time import perf_counter
from typing import Any


def solve(*, n: int) -> int:
    upper_bound_num_digits = math.ceil(math.log(n * 9**n, 10))
    return sum(
        (
            num
            for digits in itertools.combinations_with_replacement(range(10), upper_bound_num_digits)
            if (num := sum((x**n for x in digits))) > 9 and num == sum((int(x) ** n for x in str(num)))
        )
    )


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
    raise SystemExit(main(n=int(argv[1])))
