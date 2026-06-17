#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 36: Double-base Palindromes [Level 0]. """
from __future__ import annotations

import typing

from solver.runners import runner


def generate_decimal_palindromes(max_digits: int) -> typing.Generator[int, None, None]:
    """Yield every decimal palindrome up to max_digits by mirroring each left half exactly once."""
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


@runner.main
def solve(*args: str) -> str:
    """Generate decimal palindromes from their left half, then keep the binary palindromes; O(sqrt(N) log N)."""
    max_digits = runner.parse_int(args[0])

    return str(sum(
        (
            number
            for number in generate_decimal_palindromes(max_digits)
            if number == int(str(bin(number))[2:][::-1], base=2)
        )
    ))


if __name__ == "__main__":
    raise SystemExit(solve())
