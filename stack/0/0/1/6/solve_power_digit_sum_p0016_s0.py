#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0016/p0016.py
  func: solve_power_digit_sum_p0016_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, base: int, power: int) -> int:
    return sum((int(i) for i in str(base**power)))


def main() -> int:
    print(solve(base=int(argv[1]), power=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
