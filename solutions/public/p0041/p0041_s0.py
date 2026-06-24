#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 41: Pandigital Prime [Level 1]. """
from __future__ import annotations

import itertools
import typing

from solver.runners import runner


def is_prime(num: int) -> bool:
    """Trial division up to sqrt(num); fast enough as candidates stay below 8 million."""
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
    """Alias for is_prime, kept for naming parity with other solutions."""
    return is_prime(num)


nine_digits: tuple[str, ...] = ("1", "2", "3", "4", "5", "6", "7", "8", "9")


def gen_n_digit_pandigital_numbers(n: int, descending: bool = False) -> typing.Generator[int, None, None]:
    """Yield every 1..n pandigital number; reversing the digit tuple gives descending order."""
    assert 1 <= n <= 9, "n must be between 1 and 9"
    n_digits: tuple[str, ...] = nine_digits[:n]
    if descending:
        n_digits = n_digits[::-1]
    yield from (int("".join(digits)) for digits in itertools.permutations(n_digits, n))


@runner.main
def solve(*args: str) -> str:
    """Digit-sum-mod-3 pruning leaves only lengths 7 and 4; scan them in descending order and
    take the first prime via a lazy generator, so that first hit is the maximum. O(k! * sqrt(N))."""
    pandigital_primes = (
        number
        for length in (7, 4)
        for number in gen_n_digit_pandigital_numbers(length, descending=True)
        if fast_is_prime(number)
    )
    return str(next(pandigital_primes))


if __name__ == "__main__":
    raise SystemExit(solve())
