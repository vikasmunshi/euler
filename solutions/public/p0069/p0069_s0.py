#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 69: Totient Maximum [Level 2]. """
from __future__ import annotations

import typing

from solver.runners import runner


def primes_generator() -> typing.Generator[int, None, None]:
    """Yield primes lazily via an incremental sieve mapping each composite to its prime."""
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
    """Greedy primorial accumulation: n/phi(n) = prod p/(p-1) over distinct primes, so the
    maximiser under a bound is the product of the smallest consecutive primes that fits; O(1)
    since fewer than ~10 primes are ever needed."""
    limit = runner.parse_int(args[0])

    result: int = 1
    for prime_num in primes_generator():
        if (result := (result * prime_num)) > limit:
            result = result // prime_num
            break
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
