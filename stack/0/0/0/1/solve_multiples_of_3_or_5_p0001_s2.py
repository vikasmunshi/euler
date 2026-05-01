#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0001/p0001.py
  func: solve_multiples_of_3_or_5_p0001_s2
"""

from __future__ import annotations

from sys import argv


def solve(*, max_limit: int) -> int:
    return sum(range(0, max_limit, 3)) + sum(range(0, max_limit, 5)) - sum(range(0, max_limit, 15))


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
