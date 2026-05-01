#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0040/p0040.py
  func: solve_champernownes_constant_p0040_s0
"""

from __future__ import annotations

from functools import reduce
from sys import argv


def get_nth_digit_champernowne_s_constant(n: int) -> int:
    length_till_num_digits, length_with_num_digits, num_digits = (0, 0, 0)
    while length_with_num_digits < n:
        num_digits += 1
        length_till_num_digits = length_with_num_digits
        length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)
    offset_of_number = n - length_till_num_digits - 1
    digit_in_number = offset_of_number % num_digits
    number = 10 ** (num_digits - 1) + offset_of_number // num_digits
    return int(str(number)[digit_in_number])


def solve(*, i: int) -> int:
    return reduce(lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10**i) for i in range(0, i + 1)), 1)


def main() -> int:
    print(solve(i=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
