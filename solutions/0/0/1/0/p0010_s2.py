#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 10: Summation of Primes [Level 0]. """
from __future__ import annotations

import typing

from solver.runners import runner


def primes_generator() -> typing.Generator[int, None, None]:
    """Yield primes endlessly via an incremental Sieve of Eratosthenes keyed on each prime's next odd multiple."""
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
    """Sum primes below max_num from an unbounded incremental Sieve of Eratosthenes; O(n log log n)."""
    max_num = runner.parse_int(args[0])

    prime_number_gen = primes_generator()
    result: int = 0
    while (prime_number := next(prime_number_gen)) < max_num:
        result += prime_number
    return str(result)


if __name__ == "__main__":
    raise SystemExit(solve())
