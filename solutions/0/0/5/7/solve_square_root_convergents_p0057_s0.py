#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0057/p0057.py
  func: solve_square_root_convergents_p0057_s0
"""

from __future__ import annotations

from sys import argv, set_int_max_str_digits


def solve(*, expansions: int) -> int:
    numerator, denominator, result = (1, 1, 0)
    for _ in range(expansions):
        numerator, denominator = (numerator + 2 * denominator, numerator + denominator)
        try:
            result += len(str(numerator)) > len(str(denominator))
        except ValueError:
            set_int_max_str_digits(0)
            print(
                f"sys.set_int_max_str_digits(0) expansions={
                    expansions!r}, len(str(numerator))={
                    len(
                        str(numerator))!r}, len(str(denominator))={
                    len(
                        str(denominator))!r}")
            result += len(str(numerator)) > len(str(denominator))
    return result


def main() -> int:
    print(solve(expansions=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
