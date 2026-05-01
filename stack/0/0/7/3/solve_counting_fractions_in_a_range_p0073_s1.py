#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0073/p0073.py
  func: solve_counting_fractions_in_a_range_p0073_s1
"""

from __future__ import annotations

from sys import argv, setrecursionlimit


def solve(*, max_d: int) -> int:

    def recursion(lower_denominator: int, upper_denominator: int) -> int:
        if (mediant := (lower_denominator + upper_denominator)) > max_d:
            return 0
        return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)

    return recursion(lower_denominator=3, upper_denominator=2)


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(max_d=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
