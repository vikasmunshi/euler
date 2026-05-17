#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 66: Diophantine Equation [Level 11]. """
from __future__ import annotations

import fractions
import math
import operator
from sys import argv, stderr
from time import perf_counter
from typing import Any


def compute_nth_convergent(continued_fraction: tuple[int, ...], n: int) -> fractions.Fraction:
    period_length: int = len(continued_fraction) - 1
    convergent: fractions.Fraction = fractions.Fraction(continued_fraction[(n - 1) % period_length + 1], 1)
    for i in range(n - 1, 0, -1):
        term_index = (i - 1) % period_length + 1
        term = fractions.Fraction(continued_fraction[term_index], 1)
        convergent = term + fractions.Fraction(1, convergent)
    convergent = fractions.Fraction(continued_fraction[0], 1) + fractions.Fraction(1, convergent)
    return convergent


def find_fundamental_solution_to_pell_equation(d: int) -> tuple[int, int]:
    if (sqrt_d := math.sqrt(d)).is_integer():
        return (1, 0)
    continued_fraction: tuple[int, ...] = (math.floor(sqrt_d),)
    m: int = 0
    n: int = 1
    while continued_fraction[-1] != 2 * continued_fraction[0]:
        m = n * continued_fraction[-1] - m
        n = (d - m * m) // n
        continued_fraction += (math.floor((sqrt_d + m) / n),)
    if (len_continued_fraction := len(continued_fraction)) % 2 == 0:
        return compute_nth_convergent(continued_fraction, 2 * len_continued_fraction - 3).as_integer_ratio()
    else:
        return compute_nth_convergent(continued_fraction, len_continued_fraction - 2).as_integer_ratio()


def solve(*, max_d: int) -> int:
    return max(
        (
            (find_fundamental_solution_to_pell_equation(d)[0], d)
            for d in range(2, max_d + 1)
            if math.sqrt(d).is_integer() is False
        ),
        key=operator.itemgetter(0),
    )[-1]


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
    raise SystemExit(main(max_d=int(argv[1])))
