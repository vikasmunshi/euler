#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0072/p0072.py
  func: solve_counting_fractions_p0072_s0
"""

from __future__ import annotations

from sys import argv
from typing import List


def solve(*, max_d: int) -> int:
    euler_totients: List[int] = list(range(max_d + 1))
    result: int = 0
    for n in range(2, max_d + 1):
        if euler_totients[n] == n:
            for j in range(n, max_d + 1, n):
                euler_totients[j] = euler_totients[j] // n * (n - 1)
        result += euler_totients[n]
    return result


def main() -> int:
    print(solve(max_d=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
