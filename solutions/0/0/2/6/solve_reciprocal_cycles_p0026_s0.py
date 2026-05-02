#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0026/p0026.py
  func: solve_reciprocal_cycles_p0026_s0
"""

from __future__ import annotations

from math import gcd
from sys import argv
from typing import Optional


def multiplicative_order(a: int, modulus: int) -> Optional[int]:
    r = 1
    for k in range(1, modulus):
        r = r * a % modulus
        if r == 1:
            return k
    else:
        return None


def solve(*, limit: int) -> int:
    return max(
        (
            (multiplicative_order(a=10, modulus=d), d)
            for i in range(max(limit // 10, 10))
            if (d := (limit - i)) > 6 and gcd(d, 10) == 1
        )
    )[1]


def main() -> int:
    print(solve(limit=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
