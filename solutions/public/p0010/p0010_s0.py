#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 10: Summation of Primes [Level 0]. """
from __future__ import annotations

from solver.runners import runner


def primes_eratosthenes_sieve_upto_max_num(max_num: int) -> tuple[int, ...]:
    """Return every prime <= max_num via a Sieve of Eratosthenes."""
    if max_num < 2:
        return ()
    sieve = bytearray(b"\x01") * (max_num + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(max_num ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
    return tuple((i for i in range(2, max_num + 1) if sieve[i]))


@runner.main
def solve(*args: str) -> str:
    """Sum the primes up to max_num with a Sieve of Eratosthenes; O(n log log n) time, O(n) space."""
    max_num = runner.parse_int(args[0])

    return str(sum(primes_eratosthenes_sieve_upto_max_num(max_num)))


if __name__ == "__main__":
    raise SystemExit(solve())
