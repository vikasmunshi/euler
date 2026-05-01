#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0064/p0064.py
  func: solve_odd_period_square_roots_p0064_s0
"""

from __future__ import annotations

from math import isqrt, sqrt
from sys import argv


def get_period_length(n: int) -> int:
    a0 = a = isqrt(n)
    d, m, p = (1, 0, [])
    while True:
        m = d * a - m
        d = (n - m**2) // d
        a = (a0 + m) // d
        if (m, d, a) in p:
            break
        p.append((m, d, a))
    return len(p)


def solve(*, max_limit: int) -> int:
    return sum((get_period_length(n) % 2 == 1 for n in range(2, max_limit + 1) if not sqrt(n).is_integer()))


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
