#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 10: Summation of Primes [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Return every prime <= max_num via the Sieve of Sundaram (marks 2*i*j+i+j to drop odd composites)."""
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
    """Sum the primes up to max_num with the Sieve of Sundaram; O(n log n) time, O(n) space."""
    max_num = runner.parse_int(args[0])

    return str(sum(primes_sundaram_sieve(max_num)))


if __name__ == "__main__":
    raise SystemExit(solve())
