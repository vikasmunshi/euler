#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0092/p0092.py
  func: solve_square_digit_chains_p0092_s0
"""

from __future__ import annotations

from sys import argv
from typing import Dict


def show_solution() -> bool:
    return "--show" in argv


def terminates_in_89(n: int) -> bool:
    while n != 1 and n != 89:
        n, t = (0, n)
        while t:
            n, t = (n + (t % 10) ** 2, t // 10)
    return n == 89


def solve(*, power_of_10: int) -> int:
    a, sq, is89 = ([1], [x**2 for x in range(1, 10)], [False])
    results: Dict[int, int] = {}
    for n in range(1, power_of_10 + 1):
        b, a = (a, a + [0] * 81)
        is89 += map(terminates_in_89, range(len(b), len(a)))
        for i, v in enumerate(b):
            for s in sq:
                a[i + s] += v
        results[n] = sum((a[i] for i in range(len(a)) if is89[i]))
    if show_solution():
        print(f"Results for power_of_10={power_of_10}: {results}")
    return results[power_of_10]


def main() -> int:
    print(solve(power_of_10=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
