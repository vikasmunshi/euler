#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0073/p0073.py
  func: solve_counting_fractions_in_a_range_p0073_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, max_d: int) -> int:
    lower_denominator: int = 3
    upper_denominator: int = 2
    d = upper_denominator + lower_denominator * ((max_d - upper_denominator) // lower_denominator)
    prev_d = lower_denominator
    count = 0
    while d != upper_denominator:
        count += 1
        prev_d, d = (d, max_d - (max_d + prev_d) % d)
    return count


def main() -> int:
    print(solve(max_d=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
