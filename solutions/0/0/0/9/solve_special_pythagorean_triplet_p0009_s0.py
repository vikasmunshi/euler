#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0009/p0009.py
  func: solve_special_pythagorean_triplet_p0009_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, sum_sides: int) -> int:
    try:
        return next(
            (
                a * b * c
                for a in range(1, sum_sides // 4 + 1)
                for b in range(a, sum_sides // 2)
                for c in (sum_sides - a - b,)
                if a**2 + b**2 == c**2
            )
        )
    except StopIteration:
        raise ValueError(f"No Pythagorean triplet exists with sum {sum_sides}")


def main() -> int:
    print(solve(sum_sides=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
