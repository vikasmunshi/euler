#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0052/p0052.py
  func: solve_permuted_multiples_p0052_s0
"""

from __future__ import annotations

import sys
from sys import argv


def solve(*, multiples: int) -> int:
    if not (isinstance(multiples, int) and 1 < multiples < 7):
        raise ValueError("multiples must be an integer between 2 and 6, both inclusive.")
    multiples_range = tuple(range(1, multiples + 1))
    for i in range(1, sys.maxsize // multiples):
        if len({"".join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
            return i
    else:
        raise ValueError("No solution found")


def main() -> int:
    print(solve(multiples=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
