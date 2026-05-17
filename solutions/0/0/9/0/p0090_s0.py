#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 90: Cube Digit Pairs [Level 9]. """
from __future__ import annotations

import itertools
from sys import argv, stderr
from time import perf_counter
from typing import Any


def solve() -> int:
    squares: list[tuple[int, int]] = [(int((i_sq := f"{i * i:02d}")[0]), int(i_sq[1])) for i in range(1, 10)]

    def can_display(cube_digits: tuple[int, ...], digit: int) -> bool:
        return digit in cube_digits or (digit in [6, 9] and (6 in cube_digits or 9 in cube_digits))

    def can_pair_display_all(cube1: tuple[int, ...], cube2: tuple[int, ...]) -> bool:
        for first_digit, second_digit in squares:
            if not (
                can_display(cube1, first_digit)
                and can_display(cube2, second_digit)
                or (can_display(cube1, second_digit) and can_display(cube2, first_digit))
            ):
                return False
        return True

    all_cubes: list[tuple[int, ...]] = list(itertools.combinations(range(10), 6))
    cube_count: int = len(all_cubes)
    valid_arrangements: int = 0
    for i in range(cube_count):
        for j in range(i, cube_count):
            if can_pair_display_all(all_cubes[i], all_cubes[j]):
                valid_arrangements += 1
    return valid_arrangements


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
