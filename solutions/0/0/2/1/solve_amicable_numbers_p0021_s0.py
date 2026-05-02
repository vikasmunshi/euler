#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0021/p0021.py
  func: solve_amicable_numbers_p0021_s0
"""

from __future__ import annotations

from functools import lru_cache
from sys import argv


@lru_cache()
def sum_factors(n: int) -> int:
    n_sqrt = int(n**0.5)
    return 1 + sum((i + n // i for i in range(2, n_sqrt + 1) if n % i == 0)) - (n_sqrt if n_sqrt**2 == n else 0)


def solve(*, max_num: int) -> int:
    return sum((x for x in range(2, max_num + 1) if (y := sum_factors(x)) != x and sum_factors(y) == x))


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
