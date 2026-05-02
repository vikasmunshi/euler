#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0033/p0033.py
  func: solve_digit_cancelling_fractions_p0033_s0
"""

from __future__ import annotations

from fractions import Fraction
from functools import reduce


def solve() -> int:
    return reduce(
        lambda a, b: a * b,
        (
            Fraction(numerator, denominator)
            for denominator in range(2, 10)
            for numerator in range(1, denominator)
            for x in range(1, 10)
            if denominator != x != numerator
            if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator
        ),
        Fraction(1, 1),
    ).denominator


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
