#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0005/p0005.py
  func: solve_smallest_multiple_p0005_s0
"""

from __future__ import annotations

from functools import reduce
from math import gcd
from sys import argv


def solve(*, n: int) -> int:
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
