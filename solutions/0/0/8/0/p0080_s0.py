#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 80: Square Root Digital Expansion [Level 4]. """
from __future__ import annotations

from sys import argv, stderr
from time import perf_counter
from typing import Any


def sqrt_heron_method(number: int, digits: int) -> str:
    if number == 0:
        return "0" * min(1, digits)
    if number < 0:
        raise ValueError(f"Cannot calculate square root of negative number: {number}")
    number *= 10 ** (2 * digits)
    sqrt = number
    while sqrt != (sqrt := ((sqrt + number // sqrt) // 2)):
        pass
    return str(sqrt)[:digits]


def sum_digits(n: str) -> int:
    return sum((int(digit) for digit in n))


def solve(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i**0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
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
    raise SystemExit(main(digits=int(argv[1]), max_num=int(argv[2])))
