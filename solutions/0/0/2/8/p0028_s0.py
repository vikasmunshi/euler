#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 28: Number Spiral Diagonals [Level 0]. """
from __future__ import annotations

import sys
from sys import argv, stderr
from time import perf_counter
from typing import Any


def number_spiral_with_diagonal_sum(size: int) -> int:
    x, y, coordinate_map = (0, 0, {(0, 0): 1})
    for number in range(2, size**2 + 1):
        free_adjacent_coords = (c for c in ((x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)) if c not in coordinate_map)
        x, y = min(((c[0] ** 2 + c[1] ** 2, c) for c in free_adjacent_coords), key=lambda c: c[0])[1]
        coordinate_map[x, y] = number
    msg: list[str] = [f"Generated spiral for size {size} with diagonal elements highlighted in\x1b[34m blue\x1b[0m:"]
    half_size = size // 2
    for row in range(half_size, -half_size - 1, -1):
        row_values = []
        for col in range(-half_size, half_size + 1):
            value = coordinate_map.get((col, row), 0)
            if col == row or col == -row:
                row_values.append(f"\x1b[34m{value:2d}\x1b[0m")
            else:
                row_values.append(f"{value:2d}")
        msg.append(" ".join(row_values))
    diagonal_sum = sum((n for c, n in coordinate_map.items() if c[0] == c[1] or c[0] == -c[1]))
    formula_result = (size * (size * (4 * size + 3) + 8) - 9) // 6
    status = "\x1b[32m✓" if formula_result == diagonal_sum else "\x1b[31m✗"
    msg.append(f"{status} size={size!r}; formula_result={formula_result!r}; diagonal_sum={diagonal_sum!r}\x1b[0m")
    print("\n".join(msg))
    return diagonal_sum


def solve(*, size: int) -> int:
    if not isinstance(size, int) or size <= 0 or size % 2 == 0:
        raise ValueError("Size must be a positive odd integer")
    if sys.argv[-1] == "--show" and size <= 10:
        return number_spiral_with_diagonal_sum(size)
    return (size * (size * (4 * size + 3) + 8) - 9) // 6


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
    raise SystemExit(main(size=int(argv[1])))
