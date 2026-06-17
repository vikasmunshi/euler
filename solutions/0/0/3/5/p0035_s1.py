#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 35: Circular Primes [Level 1]. """
from __future__ import annotations

from primesieve import primes as sieve_primes
from solver.runners import runner


def get_rotated_numbers(*, num: int) -> set[int]:
    """Return the set of cyclic digit rotations of num."""
    str_num: str = str(num)
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


@runner.main
def solve(*args: str) -> str:
    """Keep primes whose every rotation is prime; same logic as s0 but primes come from the tuned
    primesieve library, and a set gives O(1) membership for each rotation test."""
    max_limit = runner.parse_int(args[0])

    primes = set(sieve_primes(max_limit))
    circular_primes = [
        prime
        for prime in primes
        if prime < 10
        or (
            not any((d in str(prime) for d in "024568"))
            and (not any((rotated_number not in primes for rotated_number in get_rotated_numbers(num=prime))))
        )
    ]
    return str(len(circular_primes))


if __name__ == "__main__":
    raise SystemExit(solve())
