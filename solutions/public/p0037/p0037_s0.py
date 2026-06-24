#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 37: Truncatable Primes [Level 1]. """
from __future__ import annotations

import typing

from solver.runners import runner


def primes_generator() -> typing.Generator[int, None, None]:
    """Yield primes in increasing order via Eppstein's dict-based incremental sieve; O(n log log n)."""
    yield 2
    composites: dict[int, int] = {}
    n = 3
    while True:
        if n not in composites:
            yield n
            composites[n * n] = n
        else:
            p = composites.pop(n)
            m = n + 2 * p
            while m in composites:
                m += 2 * p
            composites[m] = p
        n += 2


@runner.main
def solve(*args: str) -> str:
    """Stream primes as strings; a prime is truncatable iff every prefix/suffix already lies in the
    seen-set, so each test is O(digits) set lookups. Sorted generation guarantees those smaller
    primes are present; stop after the eleven known truncatable primes."""
    primes: set[str] = set()
    truncatable_primes: list[int] = list()
    for prime_num in primes_generator():
        prime = str(prime_num)
        primes.add(prime)
        if int(prime) < 10:
            continue
        if not any(
            (pl not in primes or pr not in primes for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))])
        ):
            truncatable_primes.append(prime_num)
        if len(truncatable_primes) == 11:
            break
    return str(sum(truncatable_primes))


if __name__ == "__main__":
    raise SystemExit(solve())
