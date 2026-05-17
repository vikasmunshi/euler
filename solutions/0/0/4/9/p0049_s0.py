#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 49: Prime Permutations [Level 1]. """
from __future__ import annotations

import collections
import itertools
from sys import argv, stderr
from time import perf_counter
from typing import Any


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


def solve(*, n: int) -> list:
    sequences: set[str] = set()
    min_n_digit_hum = 10 ** (n - 1)
    n_digit_primes: set[str] = {str(p) for p in primes_sundaram_sieve(10**n) if p > min_n_digit_hum}
    for prime in n_digit_primes:
        permuted_primes: set[str] = set(
            (p for d in itertools.permutations(prime) if (p := "".join(d)) in n_digit_primes)
        )
        if len(permuted_primes) >= 3:
            differences: dict[int, set[str]] = collections.defaultdict(set)
            for prime_i, prime_j in itertools.combinations(permuted_primes, 2):
                differences[abs(int(prime_j) - int(prime_i))].update((prime_i, prime_j))
            for difference, primes in differences.items():
                if len(primes) == 3:
                    sequences.add(" ".join(sorted(primes)))
    return sorted(sequences)


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
