#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0001/p0001.py
  func: solve_multiples_of_3_or_5_p0001_s1
"""

from __future__ import annotations

from sys import argv


def solve(*, max_limit: int) -> int:
    result: int = 0
    for term in range(0, max_limit):
        if term % 3 == 0 or term % 5 == 0:
            result += term
    return result


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
