#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 41: Pandigital Prime [Level 1]. """
from __future__ import annotations

import itertools
import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any


def is_prime(num: int) -> bool:
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


def fast_is_prime(num: int) -> bool:
    return is_prime(num)


nine_digits: tuple[str, ...] = ("1", "2", "3", "4", "5", "6", "7", "8", "9")


def gen_n_digit_pandigital_numbers(n: int, descending: bool = False) -> typing.Generator[int, None, None]:
    assert 1 <= n <= 9, "n must be between 1 and 9"
    n_digits: tuple[str, ...] = nine_digits[:n]
    if descending:
        n_digits = n_digits[::-1]
    yield from (int("".join(digits)) for digits in itertools.permutations(n_digits, n))


def solve() -> int:
    pandigital_primes = (
        number
        for length in (7, 4)
        for number in gen_n_digit_pandigital_numbers(length, descending=True)
        if fast_is_prime(number)
    )
    return next(pandigital_primes)


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
