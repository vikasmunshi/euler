#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0071/p0071.py
  func: solve_ordered_fractions_p0071_s0
"""

from __future__ import annotations

from fractions import Fraction
from sys import argv


def show_solution() -> bool:
    return "--show" in argv


def solve(*, max_d: int) -> int:
    result: Fraction = Fraction(3, 7) - Fraction(1, 7 * (max_d // 7))
    if show_solution():
        difference = Fraction(3, 7) - result
        print(
            f"Solution for max_d={
                max_d!r}: result={
                result!r} difference={
                difference!r} result.numerator={
                    result.numerator!r}")
    return result.numerator


def main() -> int:
    print(solve(max_d=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
