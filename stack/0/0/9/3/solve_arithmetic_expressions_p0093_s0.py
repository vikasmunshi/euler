#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0093/p0093.py
  func: solve_arithmetic_expressions_p0093_s0
"""

from __future__ import annotations

from functools import lru_cache
from sys import argv, setrecursionlimit
from typing import Set


def show_solution() -> bool:
    return "--show" in argv


@lru_cache(maxsize=None)
def eval_all_operations(vals: tuple[int | float, ...]) -> Set[int | float]:
    if (len_v := len(vals)) == 1:
        return {vals[0]}
    s = set()
    for i in range(len_v - 1):
        for j in range(i + 1, len_v):
            a, b = (vals[i], vals[j])
            r = tuple([vals[k] for k in range(len_v) if k not in (i, j)])
            s |= eval_all_operations(r + (a + b,))
            s |= eval_all_operations(r + (abs(a - b),))
            s |= eval_all_operations(r + (a * b,))
            if b > 0:
                s |= eval_all_operations(r + (a / b,))
            if a > 0:
                s |= eval_all_operations(r + (b / a,))
    return s


def solve() -> str:
    max_digits: str = ""
    max_length: int = 0
    max_results: Set[int] = set()
    for a in range(1, 7):
        for b in range(a + 1, 8):
            for c in range(b + 1, 9):
                for d in range(c + 1, 10):
                    results: Set[int] = {int(x) for x in eval_all_operations((a, b, c, d)) if x.is_integer()}
                    length = 0
                    while length + 1 in results:
                        length += 1
                    if length > max_length:
                        max_length, max_digits, max_results = (length, f"{a}{b}{c}{d}", results)
    if show_solution():
        print(f"max_digits={max_digits!r} max_length={max_length!r} max_results={max_results!r}")
    return max_digits


def main() -> int:
    setrecursionlimit(10**6)
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
