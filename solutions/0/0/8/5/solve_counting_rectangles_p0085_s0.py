#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0085/p0085.py
  func: solve_counting_rectangles_p0085_s0
"""

from __future__ import annotations

from functools import partial
from itertools import product
from sys import argv
from typing import Any, Dict, Tuple


def num_rectangles(height: int, width: int) -> int:
    return sum(((height - h + 1) * (width - w + 1) for w in range(1, width + 1) for h in range(1, height + 1)))


def show_solution() -> bool:
    return "--show" in argv


def delta_func(kv: Tuple[int, Any], *, target_num: int) -> int:
    return abs(kv[0] - target_num)


def solve(*, max_error: int, max_side: int, target_num_rectangles: int) -> int:
    delta = partial(delta_func, target_num=target_num_rectangles)
    results: Dict[int, Tuple[int, int, int]] = {}
    for height, width in product(range(2, max_side), repeat=2):
        results[(num := num_rectangles(height, width))] = (height, width, height * width)
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
