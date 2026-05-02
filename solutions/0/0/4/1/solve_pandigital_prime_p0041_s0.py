#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0041/p0041.py
  func: solve_pandigital_prime_p0041_s0
"""

from __future__ import annotations

from itertools import permutations
from typing import Generator


def is_prime(num: int) -> bool:
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


def fast_is_prime(num: int) -> bool:
    return is_prime(num)


nine_digits: tuple[str, ...] = ("1", "2", "3", "4", "5", "6", "7", "8", "9")


def gen_n_digit_pandigital_numbers(n: int, descending: bool = False) -> Generator[int, None, None]:
    assert 1 <= n <= 9, "n must be between 1 and 9"
    n_digits: tuple[str, ...] = nine_digits[:n]
    if descending:
        n_digits = n_digits[::-1]
    yield from (int("".join(digits)) for digits in permutations(n_digits, n))


def solve() -> int:
    pandigital_primes = (
        number
        for length in (7, 4)
        for number in gen_n_digit_pandigital_numbers(length, descending=True)
        if fast_is_prime(number)
    )
    return next(pandigital_primes)


def main() -> int:
    print(solve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
