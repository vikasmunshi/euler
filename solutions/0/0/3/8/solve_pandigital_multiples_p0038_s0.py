#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0038/p0038.py
  func: solve_pandigital_multiples_p0038_s0
"""

from __future__ import annotations


def is_nine_pandigital(n: int) -> bool:
    if n < 100000000 or n > 999999999:
        return False
    digits: list[int] = [0] * 10
    while n:
        d = n % 10
        if d == 0 or digits[d] == 1:
            return False
        digits[d] = 1
        n //= 10
    return sum(digits[1:]) == 9


def solve() -> int:
    for n, x in ((2, 9876), (3, 987), (4, 98), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)):
        while x > 0:
            number: int = int("".join([str(i * x) for i in range(1, n + 1)]))
            if is_nine_pandigital(number):
                return number
            x -= 1
    raise ValueError("No solution found")


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
