#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0077/p0077.py
  func: solve_prime_summations_p0077_s1
"""

from __future__ import annotations

from functools import lru_cache
from itertools import count
from sys import argv, setrecursionlimit


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
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


@lru_cache(maxsize=None)
def get_prime_partitions_simple_recursion(*, number: int, slots: int, safe_limit: int | None = 50) -> list[list[int]]:
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


def solve(*, num_prime_partitions: int) -> int:
    for n in count(2):
        if len(get_prime_partitions_simple_recursion(number=n, slots=n)) >= num_prime_partitions:
            return n
    return -1


def main() -> int:
    setrecursionlimit(10**6)
    print(solve(num_prime_partitions=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
