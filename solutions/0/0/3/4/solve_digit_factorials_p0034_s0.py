#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0034/p0034.py
  func: solve_digit_factorials_p0034_s0
"""

from __future__ import annotations

from itertools import combinations_with_replacement


def solve() -> int:
    upper_bound_num_digits = 7 + 1
    factorial = {"0": 1, "1": 1, "2": 2, "3": 6, "4": 24, "5": 120, "6": 720, "7": 5040, "8": 40320, "9": 362880}
    return sum(
        (
            int(num)
            for num_digits in range(2, upper_bound_num_digits)
            for digits in combinations_with_replacement("0123456789", num_digits)
            for num in (str(sum((factorial[d] for d in digits))),)
            if len(num) == num_digits
            and all((digit in num for digit in digits))
            and (num == str(sum((factorial[n] for n in num))))
        )
    )


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
