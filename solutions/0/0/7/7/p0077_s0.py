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
def num_prime_partitions_simple_recursion(*, number: int, slots: int) -> int:
    """Count prime partitions of number with parts <= slots; passing p as the next
    ceiling forces non-increasing parts, so each multiset is counted once."""
    if number < 0 or slots < 0:
        raise ValueError("number and slots must be non-negative")
    if number == 0:
        return 1
    if slots < 2:
        return 0
    result = 0
    max_num = min(number, slots)
    for n in primes_sundaram_sieve(max_num):
        result += num_prime_partitions_simple_recursion(number=number - n, slots=n)
    return result


@runner.main
def solve(*args: str) -> str:
    """Count-only memoised recursion over (remaining sum, max allowed part); first n whose
    prime-partition count reaches the threshold. O(N * pi(N)) subproblems, O(pi(N)) each."""
    num_prime_partitions = runner.parse_int(args[0])

    for n in itertools.count(1):
        if num_prime_partitions_simple_recursion(number=n, slots=n) >= num_prime_partitions:
            return str(n)
    return str(-1)


if __name__ == "__main__":
    raise SystemExit(solve())
