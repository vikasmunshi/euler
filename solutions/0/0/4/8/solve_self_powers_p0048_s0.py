#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0048/p0048.py
  func: solve_self_powers_p0048_s0
"""

from __future__ import annotations

from sys import argv


def solve(*, limit: int) -> int:
    modulo: int = 10**10
    result: int = 0
    for i in range(1, limit + 1):
        term = pow(i, i, modulo)
        result = (result + term) % modulo
    return result


def main() -> int:
    print(solve(limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
