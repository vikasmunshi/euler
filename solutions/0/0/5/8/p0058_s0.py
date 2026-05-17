#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 58: Spiral Primes [Level 2]. """
from __future__ import annotations

import typing
from sys import argv, stderr
from time import perf_counter
from typing import Any


def generator_spiral_corners() -> typing.Generator[tuple[int, int, int, int, int], None, None]:
    layer = 0
    while layer := (layer + 1):
        side_length = 2 * layer + 1
        side_length_min_1 = side_length - 1
        bottom_right = side_length**2
        bottom_left = bottom_right - side_length_min_1
        top_left = bottom_left - side_length_min_1
        top_right = top_left - side_length_min_1
        yield (side_length, bottom_right, bottom_left, top_left, top_right)


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


def solve(*, threshold: float) -> int:
    num_prime_diagonals: int = 0
    num_diagonal_elements: int = 1
    for side_length, bottom_right, bottom_left, top_left, top_right in generator_spiral_corners():
        num_diagonal_elements += 4
        for corner in (bottom_right, bottom_left, top_left, top_right):
            num_prime_diagonals += is_prime(corner)
        if num_prime_diagonals / num_diagonal_elements < threshold:
            return side_length
    else:
        raise ValueError("No solution found")


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
    raise SystemExit(main(threshold=float(argv[1])))
