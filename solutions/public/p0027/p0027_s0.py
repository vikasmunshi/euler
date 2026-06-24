#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 27: Quadratic Primes [Level 1]. """
from __future__ import annotations

from solver.runners import runner


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Return all primes <= max_num via the Sieve of Sundaram (odd-only marking)."""
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


def is_prime(num: int) -> bool:
    """Test primality by trial division up to sqrt(num); O(sqrt(num))."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


def prime_run(a: int, b: int) -> int:
    """Length of the unbroken prime run of |n^2 + a*n + b| for n = 0, 1, 2, ..."""
    x = 0
    while is_prime(abs(x**2 + a * x + b)):
        x += 1
    return x


@runner.main
def solve(*args: str) -> str:
    """Brute-force scan pruned by the n=0 constraint (b must be prime) and a-parity.

    Since n=0 yields b, only prime b can start a run; iterate non-negative
    magnitudes of a and apply the four sign variants. O(P * A * R * sqrt(V_max)).
    """
    max_limit = runner.parse_int(args[0])

    return str(max(
        [
            max(
                (prime_run(a, b), a * b),
                (prime_run(a, -b), -a * b),
                (prime_run(-a, -b), a * b),
                (prime_run(-a, b), -a * b),
            )
            for b in primes_sundaram_sieve(max_limit)
            for a in range(0 if b == 2 else 1, max_limit, 2)
        ]
    )[1])


if __name__ == "__main__":
    raise SystemExit(solve())
