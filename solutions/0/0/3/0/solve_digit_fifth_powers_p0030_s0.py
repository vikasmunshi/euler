#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0030/p0030.py
  func: solve_digit_fifth_powers_p0030_s0
"""

from __future__ import annotations

from itertools import combinations_with_replacement
from math import ceil, log
from sys import argv


def solve(*, n: int) -> int:
    upper_bound_num_digits = ceil(log(n * 9**n, 10))
    return sum(
        (
            num
            for digits in combinations_with_replacement(range(10), upper_bound_num_digits)
            if (num := sum((x**n for x in digits))) > 9 and num == sum((int(x) ** n for x in str(num)))
        )
    )


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
