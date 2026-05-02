#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0015/p0015.py
  func: solve_lattice_paths_p0015_s0
"""

from __future__ import annotations

from math import factorial
from sys import argv


def solve(*, lattice_size: int) -> int:
    return factorial(2 * lattice_size) // factorial(lattice_size) ** 2


def main() -> int:
    print(solve(lattice_size=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
