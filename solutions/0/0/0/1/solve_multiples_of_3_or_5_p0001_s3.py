#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0001/p0001.py
  func: solve_multiples_of_3_or_5_p0001_s3
"""

from __future__ import annotations

from sys import argv
from typing import Generator


def generate_arithmetic_series_range(common_difference: int, *, max_limit: int) -> Generator[int, None, None]:
    for term in range(0, max_limit, common_difference):
        yield term


def solve(*, max_limit: int) -> int:
    return (
        sum(generate_arithmetic_series_range(3, max_limit=max_limit))
        + sum(generate_arithmetic_series_range(5, max_limit=max_limit))
        - sum(generate_arithmetic_series_range(15, max_limit=max_limit))
    )


def main() -> int:
    print(solve(max_limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
