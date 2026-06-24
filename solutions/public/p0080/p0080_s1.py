#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 80: Square Root Digital Expansion [Level 4]. """
from __future__ import annotations

from solver.runners import runner


def sum_digits(n: str) -> int:
    """Sum the decimal digits of a digit string."""
    return sum((int(digit) for digit in n))


def sqrt_binary_search(number: int, digits: int) -> str:
    """Return the first `digits` significant digits of sqrt(number) as floor(sqrt(number *
    10^(2*digits))) by binary search on low^2 <= scaled < high^2; ~log2(sqrt(scaled)) steps."""
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


@runner.main
def solve(*args: str) -> str:
    """Sum digit sums of the first `digits` decimals of every irrational sqrt(i) for i in
    [2, max_num], each via binary-search integer sqrt of the scaled value; O(N * d^2)."""
    digits = runner.parse_int(args[0])
    max_num = runner.parse_int(args[1])

    result: int = 0
    for i in range(2, max_num + 1):
        if i**0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_binary_search(i, digits))
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
