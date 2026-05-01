#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0055/p0055.py
  func: solve_lychrel_numbers_p0055_s0
"""

from __future__ import annotations

from sys import argv


def is_lychrel(*, number: int, max_iterations: int) -> bool:
    for _ in range(max_iterations):
        number += int(str(number)[::-1])
        if str(number) == str(number)[::-1]:
            return False
    else:
        return True


def solve(*, max_iterations: int, max_limit: int) -> int:
    return sum((is_lychrel(number=i, max_iterations=max_iterations) for i in range(1, max_limit + 1)))


def main() -> int:
    print(solve(max_iterations=int(argv[1]), max_limit=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
