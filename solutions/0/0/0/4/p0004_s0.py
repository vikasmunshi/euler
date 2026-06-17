#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 4: Largest Palindrome Product [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def is_palindromic(*, number: int) -> bool:
    str_number: str = str(number)
    return str_number == "".join(reversed(str_number))


@runner.main
def solve(*args: str) -> str:
    """Descending pruned search for the largest palindromic product of two n-digit numbers.

    Every even-length palindrome is divisible by 11, so one factor must supply that 11:
    when `a` is not a multiple of 11 the inner factor `b` steps by 11, skipping ten of
    every eleven candidates. Iterating downward with a monotone `a*b` early exit prunes
    the rest. O(d^2 / 11) worst case in the count d = 9*10^(n-1) of n-digit numbers."""
    n = runner.parse_int(args[0])

    largest_palindrome: int = 0
    a_max: int = 0
    b_max: int = 0
    max_number: int = 10**n - 1
    min_number: int = 10 ** (n - 1)
    max_multiple_11 = max_number - max_number % 11
    for a in range(max_number, min_number, -1):
        a_is_multiple_11 = a % 11 == 0
        for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
            ab = a * b
            if ab <= largest_palindrome:
                break
            if is_palindromic(number=ab):
                a_max, b_max, largest_palindrome = (a, b, ab)
    if runner.show:
        print(
            f"Largest palindrome that is a multiple of two {n}-digit numbers is {largest_palindrome} ({a_max}x{b_max})"
        )
    return str(largest_palindrome)


if __name__ == "__main__":
    raise SystemExit(solve())
