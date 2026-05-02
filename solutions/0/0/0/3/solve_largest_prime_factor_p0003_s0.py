#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0003/p0003.py
  func: solve_largest_prime_factor_p0003_s0
"""

from __future__ import annotations

from sys import argv


def reduce(num: int, divisor: int) -> int:
    num //= divisor
    while num % divisor == 0:
        num //= divisor
    return num


def solve(*, number: int) -> int:
    if number % 2 == 0:
        remaining_number = reduce(number, 2)
        largest_factor = 2
    else:
        remaining_number = number
        largest_factor = 1
    current_factor = 3
    search_limit = int(remaining_number**0.5)
    while remaining_number > 1 and current_factor <= search_limit:
        if remaining_number % current_factor == 0:
            remaining_number = reduce(remaining_number, current_factor)
            largest_factor = current_factor
            search_limit = int(remaining_number**0.5)
        current_factor += 2
    return remaining_number if remaining_number > 1 else largest_factor


def main() -> int:
    print(solve(number=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
