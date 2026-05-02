#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0019/p0019.py
  func: solve_counting_sundays_p0019_s0
"""

from __future__ import annotations

from datetime import date
from sys import argv


def solve(*, end_year: int, start_year: int) -> int:
    return sum((date(y, m, day=1).isoweekday() == 7 for m in range(1, 13) for y in range(start_year, end_year + 1)))


def main() -> int:
    print(solve(end_year=int(argv[1]), start_year=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
