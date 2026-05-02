#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0004/p0004.py
  func: solve_largest_palindrome_product_p0004_s0
"""

from __future__ import annotations

from sys import argv


def show_solution() -> bool:
    return "--show" in argv


def is_palindromic(*, number: int) -> bool:
    str_number: str = str(number)
    return str_number == "".join(reversed(str_number))


def solve(*, n: int) -> int:
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
    if show_solution():
        print(
            f"Largest palindrome that is a multiple of two {n}-digit numbers is {largest_palindrome} ({a_max}x{b_max})"
        )
    return largest_palindrome


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
