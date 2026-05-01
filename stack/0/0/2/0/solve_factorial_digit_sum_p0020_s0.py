#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0020/p0020.py
  func: solve_factorial_digit_sum_p0020_s0
"""

from __future__ import annotations

from math import factorial
from sys import argv


def solve(*, n: int) -> int:
    return sum((int(d) for d in str(factorial(n))))


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
