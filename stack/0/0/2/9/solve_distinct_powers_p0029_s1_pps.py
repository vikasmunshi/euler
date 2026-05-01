#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0029/p0029.py
  func: solve_distinct_powers_p0029_s1_pps
"""

from __future__ import annotations

from sys import argv

import pyprimesieve as pps


def solve(*, a_min: int, a_max: int, b_min: int, b_max: int) -> int:
    if min(a_max, b_max) > 100:
        unique_powers = set()
        for a in range(a_min, a_max + 1):
            prime_factors = pps.factorize(a)
            for b in range(b_min, b_max + 1):
                signature = tuple(((prime, power * b) for prime, power in prime_factors))
                unique_powers.add(signature)
        return len(unique_powers)
    else:
        return len({a**b for a in range(a_min, a_max + 1) for b in range(a_min, a_max + 1)})


def main() -> int:
    print(solve(a_min=int(argv[1]), a_max=int(argv[2]), b_min=int(argv[3]), b_max=int(argv[4])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
