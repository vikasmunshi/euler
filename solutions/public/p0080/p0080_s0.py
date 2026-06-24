#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 80: Square Root Digital Expansion [Level 4]. """
from __future__ import annotations

from solver.runners import runner


def sqrt_heron_method(number: int, digits: int) -> str:
    """Return the first `digits` significant digits of sqrt(number) as floor(sqrt(number *
    10^(2*digits))) via Heron's method; quadratic convergence, ~7 iterations for 100 digits."""
    if number == 0:
        return "0" * min(1, digits)
    if number < 0:
        raise ValueError(f"Cannot calculate square root of negative number: {number}")
    number *= 10 ** (2 * digits)
    sqrt = number
    while sqrt != (sqrt := ((sqrt + number // sqrt) // 2)):
        pass
    return str(sqrt)[:digits]


def sum_digits(n: str) -> int:
    """Sum the decimal digits of a digit string."""
    return sum((int(digit) for digit in n))


@runner.main
def solve(*args: str) -> str:
    """Sum digit sums of the first `digits` decimals of every irrational sqrt(i) for i in
    [2, max_num], each via Heron integer sqrt of the scaled value; O(N * d^2)."""
    digits = runner.parse_int(args[0])
    max_num = runner.parse_int(args[1])

    result: int = 0
    for i in range(2, max_num + 1):
        if i**0.5 % 1 == 0:
            continue
        result += sum_digits(sqrt_heron_method(i, digits))
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
