#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 40: Champernowne's Constant [Level 1]. """
from __future__ import annotations

import functools

from solver.runners import runner


def get_nth_digit_champernowne_s_constant(n: int) -> int:
    """Locate digit n by walking d-digit bands (length d*9*10^(d-1)), then floor-div/mod; O(log n)."""
    length_till_num_digits, length_with_num_digits, num_digits = (0, 0, 0)
    while length_with_num_digits < n:
        num_digits += 1
        length_till_num_digits = length_with_num_digits
        length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)
    offset_of_number = n - length_till_num_digits - 1
    digit_in_number = offset_of_number % num_digits
    number = 10 ** (num_digits - 1) + offset_of_number // num_digits
    return int(str(number)[digit_in_number])


@runner.main
def solve(*args: str) -> str:
    """Fold the product of band-walk lookups at positions 10^0..10^i; O(i log(10^i)) integer ops."""
    i = runner.parse_int(args[0])

    return str(functools.reduce(
        lambda x, y: x * y, (get_nth_digit_champernowne_s_constant(10**i) for i in range(0, i + 1)), 1
    ))


if __name__ == "__main__":
    raise SystemExit(solve())
