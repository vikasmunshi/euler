#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0080/p0080.py
  func: solve_square_root_digital_expansion_p0080_s1
"""

from __future__ import annotations

from sys import argv


def sum_digits(n: str) -> int:
    return sum((int(digit) for digit in n))


def sqrt_binary_search(number: int, digits: int) -> str:
    if number == 0:
        return "0" * min(1, digits)
    if number < 0:
        raise ValueError(f"Cannot calculate square root of negative number: {number}")
    scaled_number = number * 10 ** (2 * digits)
    low = 0
    high = scaled_number
    while high - low > 1:
        mid = (low + high) // 2
        if mid * mid <= scaled_number:
            low = mid
        else:
            high = mid
    return str(low)[:digits]


def solve(*, digits: int, max_num: int) -> int:
    result: int = 0
    for i in range(2, max_num + 1):
        if i**0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_binary_search(i, digits))
    return result


def main() -> int:
    print(solve(digits=int(argv[1]), max_num=int(argv[2])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
