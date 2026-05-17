#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 37: Truncatable Primes [Level 1]. """
from __future__ import annotations

import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any


def primes_generator() -> typing.Generator[int, None, None]:
    yield 2
    composites: dict[int, int] = {}
    n = 3
    while True:
        if n not in composites:
            yield n
            composites[n * n] = n
        else:
            p = composites.pop(n)
            m = n + 2 * p
            while m in composites:
                m += 2 * p
            composites[m] = p
        n += 2


def solve() -> int:
    primes: set[str] = set()
    truncatable_primes: list[int] = list()
    for prime_num in primes_generator():
        prime = str(prime_num)
        primes.add(prime)
        if int(prime) < 10:
            continue
        if not any(
            (pl not in primes or pr not in primes for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))])
        ):
            truncatable_primes.append(prime_num)
        if len(truncatable_primes) == 11:
            break
    return sum(truncatable_primes)


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
