#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 35: Circular Primes [Level 1]. """
from __future__ import annotations

from solver.runners import runner


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Sieve of Sundaram over odd numbers; returns all primes up to max_num."""
    if max_num < 2:
        return ()
    n = (max_num - 1) // 2
    marked = bytearray(n + 1)
    for i in range(1, n + 1):
        j = i
        while i + j + 2 * i * j <= n:
            marked[i + j + 2 * i * j] = 1
            j += 1
    primes = [2] if max_num >= 2 else []
    primes.extend((2 * i + 1 for i in range(1, n + 1) if not marked[i]))
    return tuple(primes)


def get_rotated_numbers(*, num: int) -> set[int]:
    """Return the set of cyclic digit rotations of num."""
    str_num: str = str(num)
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


@runner.main
def solve(*args: str) -> str:
    """Sieve primes, then keep those whose every rotation is prime; multi-digit ones use only
    {1,3,7,9} (the digit filter prunes the rest), so set membership makes each test O(1)."""
    max_limit = runner.parse_int(args[0])

    primes = set(primes_sundaram_sieve(max_limit))
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
