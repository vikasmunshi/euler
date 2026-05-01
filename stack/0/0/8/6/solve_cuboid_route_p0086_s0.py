#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0086/p0086.py
  func: solve_cuboid_route_p0086_s0
"""

from __future__ import annotations

from itertools import count
from math import sqrt
from sys import argv


def solve(*, target_solutions: int) -> int:
    result: int = 0
    for a in count(1):
        for b_plus_c in range(1, 2 * a + 1):
            if sqrt(a**2 + b_plus_c**2).is_integer():
                result += b_plus_c // 2 if b_plus_c <= a + 1 else (2 * a - b_plus_c + 2) // 2
                if result >= target_solutions:
                    return a
    return -1


def main() -> int:
    print(solve(target_solutions=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
