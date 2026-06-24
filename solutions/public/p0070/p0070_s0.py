#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 70: Totient Permutation [Level 4]. """
from __future__ import annotations

import typing

from solver.runners import runner


def primes_generator() -> typing.Generator[int, None, None]:
    """Lazily yield primes via the postponed-composites incremental sieve; no upfront bound needed."""
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
    """Search semiprimes n = p1*p2 with both primes near sqrt(limit), since n/phi(n) = prod p/(p-1)
    is minimised by few large factors; phi(p1*p2) = (p1-1)*(p2-1) needs no factorisation. Bounding
    p1 to [sqrt(limit)/2, sqrt(limit)] and p2 to (p1+2, limit/p1] keeps the search to a narrow band."""
    limit = runner.parse_int(args[0])

    min_ratio: float = float("inf")
    min_n: int = 0
    sqrt_n = int(limit**0.5)
    min_prime_1, max_prime_1 = (sqrt_n // 2, sqrt_n)
    for prime_1 in (p for p in primes_generator() if p > min_prime_1):
        if prime_1 > max_prime_1:
            break
        min_prime_2, max_prime_2 = (prime_1 + 2, int(limit / prime_1))
        for prime_2 in (p for p in primes_generator() if p > min_prime_2):
            if prime_2 > max_prime_2:
                break
            if sorted(str((number := (prime_1 * prime_2)))) == sorted(
                str((totient := ((prime_1 - 1) * (prime_2 - 1))))
            ):
                if (ratio := (number / totient)) < min_ratio:
                    min_ratio, min_n = (ratio, number)
    return str(min_n)


if __name__ == "__main__":
    raise SystemExit(solve())
