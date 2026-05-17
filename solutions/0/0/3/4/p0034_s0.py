#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 34: Digit Factorials [Level 0]. """
from __future__ import annotations

import itertools
from sys import argv, stderr
from time import perf_counter
from typing import Any


def solve() -> int:
    upper_bound_num_digits = 7 + 1
    factorial = {"0": 1, "1": 1, "2": 2, "3": 6, "4": 24, "5": 120, "6": 720, "7": 5040, "8": 40320, "9": 362880}
    return sum(
        (
            int(num)
            for num_digits in range(2, upper_bound_num_digits)
            for digits in itertools.combinations_with_replacement("0123456789", num_digits)
            for num in (str(sum((factorial[d] for d in digits))),)
            if len(num) == num_digits
            and all((digit in num for digit in digits))
            and (num == str(sum((factorial[n] for n in num))))
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
    raise SystemExit(main())
