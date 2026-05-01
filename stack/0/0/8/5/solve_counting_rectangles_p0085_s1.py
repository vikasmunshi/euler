#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0085/p0085.py
  func: solve_counting_rectangles_p0085_s1
"""

from __future__ import annotations

from bisect import bisect_left
from functools import partial
from sys import argv
from typing import Any, Dict, Tuple


def num_rectangles_along_axis(length: int) -> int:
    return sum((length - num + 1 for num in range(1, length + 1)))


def delta_func(kv: Tuple[int, Any], *, target_num: int) -> int:
    return abs(kv[0] - target_num)


def show_solution() -> bool:
    return "--show" in argv


def solve(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
    delta = partial(delta_func, target_num=target_num_rectangles)
    results: Dict[int, Tuple[int, int, int]] = {}
    numbers: Tuple[int, ...] = tuple((num_rectangles_along_axis(length) for length in range(1, max_side)))
    len_numbers = len(numbers)
    num: int = 0
    for width, num_width in enumerate(numbers, start=1):
        j = bisect_left(a=numbers, x=target_num_rectangles // num_width)
        for height in (j + 1, j + 2):
            if 0 <= height - 1 < len_numbers:
                results[(num := (numbers[height - 1] * num_width))] = (height, width, height * width)
        if delta((num, None)) <= max_error:
            break
    if show_solution():
        result = min(results.items(), key=delta)
        print(f"Grid with {result[0]} rectangles: {result[1]}")
    return min(results.items(), key=delta)[1][2]


def main() -> int:
    print(solve(max_error=int(argv[1]), max_side=int(argv[2]), target_num_rectangles=int(argv[3])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
