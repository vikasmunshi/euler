#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 87: Prime Power Triples [Level 3]. """
from __future__ import annotations

import math
import typing

from solver.runners import runner


def prime_powers(primes: tuple[int, ...], exponent: int) -> typing.Generator[int, None, None]:
    """Lazily yield base**exponent for each prime, so early loop breaks skip unused powers."""
    for base in primes:
        yield (base**exponent)


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Return all primes up to max_num via the Sieve of Sundaram (unmarked k maps to odd prime 2k+1)."""
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


@runner.main
def solve(*args: str) -> str:
    """Enumerate p^2 + q^3 + r^4 over primes up to sqrt(N), dedup the distinct sums below N in a set.

    Ascending prime lists let each nested loop break once its partial sum exceeds the budget, so the
    nominally cubic search visits only the few million productive triples; one sieve to sqrt(N) covers
    all three exponent roles since the square term imposes the weakest bound on the base.
    """
    max_num = runner.parse_int(args[0])

    primes: tuple[int, ...] = primes_sundaram_sieve(int(math.sqrt(max_num)))
    numbers = set()
    max_quadruple_cube: int = max_num - 4
    max_quadruple: int = max_quadruple_cube - 8
    for quadruple in prime_powers(primes, 4):
        if quadruple > max_quadruple:
            break
        for cube in prime_powers(primes, 3):
            if (quadruple_cube := (quadruple + cube)) > max_quadruple_cube:
                break
            for square in prime_powers(primes, 2):
                if (number := (quadruple_cube + square)) >= max_num:
                    break
                numbers.add(number)
    return str(len(numbers))


if __name__ == "__main__":
    raise SystemExit(solve())
