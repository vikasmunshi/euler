#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 77: Prime Summations [Level 4]. """
from __future__ import annotations

import functools
import itertools

from solver.runners import runner


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Return all primes up to max_num via the Sieve of Sundaram (marks i + j + 2ij)."""
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


@functools.lru_cache(maxsize=None)
def get_prime_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
    """Build every prime partition of number with parts <= slots, prepending each chosen prime
    to the sub-partitions of the remainder; safe_limit guards against explosive growth."""
    if safe_limit and number > safe_limit:
        raise OverflowError(f"number must be less than safe_limit={safe_limit!r}")
    if number < 0 or slots < 0:
        raise ValueError("number and slots must be non-negative")
    if number < 2 or slots < 2:
        return []
    prime_partitions: list[list[int]] = []
    max_num = min(number, slots)
    for n in primes_sundaram_sieve(max_num):
        if n == number:
            prime_partitions.append([n])
        else:
            for partition in get_prime_partitions_simple_recursion(
                number=number - n, slots=min(number - n, n), safe_limit=safe_limit
            ):
                prime_partitions.append([n] + partition)
    for partition in prime_partitions:
        assert sum(partition) == number, f"partition={partition!r} sum(partition)={sum(partition)!r} number={number!r}"
    return prime_partitions


@runner.main
def solve(*args: str) -> str:
    """Enumeration-based memoised recursion: build all prime partitions and take the length of the
    first n whose list reaches the threshold. Far slower than counting; safe_limit caps the search."""
    num_prime_partitions = runner.parse_int(args[0])

    for n in itertools.count(2):
        if len(get_prime_partitions_simple_recursion(number=n, slots=n)) >= num_prime_partitions:
            return str(n)
    return str(-1)


if __name__ == "__main__":
    raise SystemExit(solve())
