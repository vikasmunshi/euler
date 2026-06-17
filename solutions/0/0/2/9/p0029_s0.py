#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 29: Distinct Powers [Level 1]. """
from __future__ import annotations

from solver.runners import runner


def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
    """Factorize n by trial division into a tuple of (prime, exponent) pairs; O(sqrt(n))."""
    if n <= 1:
        return ()
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                n //= d
                exp += 1
            factors.append((d, exp))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return tuple(factors)


@runner.main
def solve(*args: str) -> str:
    """Count distinct a^b by deduplicating in a set; O(a_max * b_max) insertions dominate.

    Small bounds key on the exact big-integer value; large bounds key on the
    prime-factorization signature (prime, exponent*b), equal exactly when the
    powers are equal, avoiding thousand-digit numbers.
    """
    a_min = runner.parse_int(args[0])
    a_max = runner.parse_int(args[1])
    b_min = runner.parse_int(args[2])
    b_max = runner.parse_int(args[3])

    if min(a_max, b_max) > 100:
        unique_powers = set()
        for a in range(a_min, a_max + 1):
            prime_factors = prime_factorization(a)
            for b in range(b_min, b_max + 1):
                signature = tuple(((prime, power * b) for prime, power in prime_factors))
                unique_powers.add(signature)
        return str(len(unique_powers))
    else:
        return str(len({a**b for a in range(a_min, a_max + 1) for b in range(b_min, b_max + 1)}))


if __name__ == "__main__":
    raise SystemExit(solve())
