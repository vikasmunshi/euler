#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0063/p0063.py
  func: solve_powerful_digit_counts_p0063_s0
"""

from __future__ import annotations

from math import ceil
from sys import argv
from typing import Tuple


def show_solution() -> bool:
    return "--show" in argv


def n_digit_nth_powers(n: int) -> Tuple[int, ...]:
    start_range: int = ceil((10 ** (n - 1)) ** (1 / n))
    stop_range: int = ceil((10**n - 1) ** (1 / n)) + 1
    return tuple((r for i in range(start_range, stop_range) if len(str((r := (i**n)))) == n))


def solve() -> int:
    result: int = 0
    n: int = 1
    while solutions := n_digit_nth_powers(n):
        result += len(solutions)
        n += 1
        if show_solution():
            print(f"n={n!r} len(solutions)={len(solutions)!r} solutions={solutions!r} ")
    return result


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
