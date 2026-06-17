#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 3: Largest Prime Factor [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def reduce(num: int, divisor: int) -> int:
    """Divide num by divisor repeatedly, returning the part coprime to divisor."""
    num //= divisor
    while num % divisor == 0:
        num //= divisor
    return num


@runner.main
def solve(*args: str) -> str:
    """Trial division with full reduction of each factor found; O(sqrt(n)) worst
    case, far less once a large prime cofactor remains. Removing every factor in
    increasing order means each surviving divisor is prime, so no primality test
    is needed; the search ceiling is recomputed from the shrinking remainder."""
    number = runner.parse_int(args[0])

    if number % 2 == 0:
        remaining_number = reduce(number, 2)
        largest_factor = 2
    else:
        remaining_number = number
        largest_factor = 1
    current_factor = 3
    search_limit = int(remaining_number**0.5)
    while remaining_number > 1 and current_factor <= search_limit:
        if remaining_number % current_factor == 0:
            remaining_number = reduce(remaining_number, current_factor)
            largest_factor = current_factor
            search_limit = int(remaining_number**0.5)
        current_factor += 2
    return str(remaining_number if remaining_number > 1 else largest_factor)


if __name__ == "__main__":
    raise SystemExit(solve())
