#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0001/p0001.py
  func: solve_multiples_of_3_or_5_p0001_s0
"""

from __future__ import annotations

from sys import argv


def sum_arithmetic_series(common_difference: int, *, max_limit: int) -> int:
    n = (max_limit - 1) // common_difference
    return common_difference * (n * (n + 1)) // 2


def solve(*, max_limit: int) -> int:
    return (
        sum_arithmetic_series(3, max_limit=max_limit)
        + sum_arithmetic_series(5, max_limit=max_limit)
        - sum_arithmetic_series(15, max_limit=max_limit)
    )


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
