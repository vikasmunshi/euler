#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 65: Convergents of $e$ [Level 2]. """
from __future__ import annotations

import fractions
import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any


def e_denominator(n: int) -> int:
    if n == 1:
        return 2
    elif n % 3 == 0:
        return 2 * n // 3
    else:
        return 1


def nth_convergent_of_e(n: int, *, _n: int = 1) -> fractions.Fraction | int:
    if n == _n:
        return e_denominator(_n)
    return e_denominator(_n) + fractions.Fraction(1, nth_convergent_of_e(n, _n=_n + 1))


def sum_digits(n: int) -> int:
    total: int = 0
    while n:
        total += n % 10
        n //= 10
    return total


def solve(*, convergent_num: int) -> int:
    return sum_digits(nth_convergent_of_e(convergent_num).numerator)


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
    sys.setrecursionlimit(10**6)
    raise SystemExit(main(convergent_num=int(argv[1])))
