#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 62: Cubic Permutations [Level 2]. """
from __future__ import annotations

import collections
import math
import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any


def n_digit_cubes(digit_length_n: int) -> tuple[int, ...]:
    start_range: int = math.ceil((10 ** (digit_length_n - 1)) ** (1 / 3))
    stop_range: int = math.ceil((10**digit_length_n - 1) ** (1 / 3)) + 1
    return tuple((i**3 for i in range(start_range, stop_range)))


def solve(*, num_permutations: int) -> int:
    digit_length: int = 2
    while True:
        cube_numbers: tuple[int, ...] = n_digit_cubes(digit_length)
        permuted_cubes: dict[str, list[int]] = collections.defaultdict(list)
        for cube_number in cube_numbers:
            permuted_cubes["".join(sorted(str(cube_number)))].append(cube_number)
        solutions: set[int] = set((min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations))
        if solutions:
            if sys.argv[-1] == "--show":
                print(f"Found {len(solutions)} cubes with {num_permutations} permutations of digits: {digit_length}")
                print(f"solutions={solutions!r}")
            return min(solutions)
        digit_length += 1


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
    raise SystemExit(main(num_permutations=int(argv[1])))
