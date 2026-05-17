#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 87: Prime Power Triples [Level 3]. """
from __future__ import annotations

import math
import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any


def prime_powers(primes: tuple[int, ...], exponent: int) -> typing.Generator[int, None, None]:
    for base in primes:
        yield (base**exponent)


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    if max_num < 2:
        return ()
    n = (max_num - 1) // 2
    marked = bytearray(n + 1)
    for i in range(1, n + 1):
        j = i
        while i + j + 2 * i * j <= n:
            marked[i + j + 2 * i * j] = 1
            j += 1
    primes = [2] if max_num >= 2 else []
    primes.extend((2 * i + 1 for i in range(1, n + 1) if not marked[i]))
    return tuple(primes)


def solve(*, max_num: int) -> int:
    primes: tuple[int, ...] = primes_sundaram_sieve(int(math.sqrt(max_num)))
    numbers = set()
    max_quadruple_cube: int = max_num - 4
    max_quadruple: int = max_quadruple_cube - 8
    for quadruple in prime_powers(primes, 4):
        if quadruple > max_quadruple:
            break
        for cube in prime_powers(primes, 3):
            if (quadruple_cube := (quadruple + cube)) > max_quadruple_cube:
                break
            for square in prime_powers(primes, 2):
                if (number := (quadruple_cube + square)) >= max_num:
                    break
                numbers.add(number)
    return len(numbers)


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
    raise SystemExit(main(max_num=int(argv[1])))
