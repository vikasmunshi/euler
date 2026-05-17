#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 18: Maximum Path Sum I [Level 1]. """
from __future__ import annotations

import copy
from sys import argv, stderr
from time import perf_counter
from typing import Any

TRIANGLE_A = ("3\n"
              "7 4\n"
              "2 4 6\n"
              "8 5 9 3\n")
TRIANGLE_B = ("75\n"
              "95 64\n"
              "17 47 82\n"
              "18 35 87 10\n"
              "20 04 82 47 65\n"
              "19 01 23 75 03 34\n"
              "88 02 77 73 07 63 67\n"
              "99 65 04 28 06 16 70 92\n"
              "41 41 26 56 83 40 80 70 33\n"
              "41 48 72 33 47 32 37 16 94 29\n"
              "53 71 44 65 25 43 91 52 97 51 14\n"
              "70 11 33 28 77 73 17 78 39 68 17 57\n"
              "91 71 52 38 17 14 91 43 58 50 27 29 48\n"
              "63 66 04 68 89 53 67 30 73 16 69 87 40 31\n"
              "04 62 98 27 23 09 70 98 73 93 38 53 60 04 23\n")


def text2triangle(text: str) -> list[list[int]]:
    return [[int(num) for num in line.split(" ")] for line in text.splitlines() if line != ""]


def max_path_sum_triangle(triangle: list[list[int]]) -> int:
    triangle = copy.deepcopy(triangle)
    while len(triangle) > 1:
        triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
        del triangle[-1]
    return triangle[0][0]


def solve(*, triangle_str: str) -> int:
    triangle_str = TRIANGLE_A if triangle_str == "TRIANGLE_A" else TRIANGLE_B if triangle_str == "TRIANGLE_B" else ""
    triangle: list[list[int]] = text2triangle(triangle_str)
    return max_path_sum_triangle(triangle)


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
    raise SystemExit(main(triangle_str=str(argv[1])))
