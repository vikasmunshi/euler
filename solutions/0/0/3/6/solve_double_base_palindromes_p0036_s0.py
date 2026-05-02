#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0036/p0036.py
  func: solve_double_base_palindromes_p0036_s0
"""

from __future__ import annotations

from sys import argv
from typing import Generator


def generate_decimal_palindromes(max_digits: int) -> Generator[int, None, None]:
    for digit in range(1, 10):
        yield digit
    for digits in range(1, 10 ** (max_digits // 2)):
        digits_str = str(digits)
        digits_rev = digits_str[::-1]
        num_digits = len(digits_str)
        yield int(digits_str + digits_rev)
        if 2 * num_digits < max_digits:
            for mid_digit in "0123456789":
                yield int(digits_str + mid_digit + digits_rev)


def solve(*, max_digits: int) -> int:
    return sum(
        (
            number
            for number in generate_decimal_palindromes(max_digits)
            if number == int(str(bin(number))[2:][::-1], base=2)
        )
    )


def main() -> int:
    print(solve(max_digits=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
