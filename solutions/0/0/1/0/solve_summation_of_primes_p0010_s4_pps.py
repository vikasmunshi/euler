#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py
  func: solve_summation_of_primes_p0010_s4_pps
"""

from __future__ import annotations

from sys import argv

import pyprimesieve as pps


def solve(*, max_num: int) -> int:
    return pps.primes_sum(max_num)


def main() -> int:
    print(solve(max_num=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
