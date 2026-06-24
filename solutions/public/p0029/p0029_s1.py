#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 29: Distinct Powers [Level 1]. """
from __future__ import annotations

from primesieve import primes
from solver.runners import runner


def factorize(n: int, sieve_primes: list[int]) -> list[tuple[int, int]]:
    """Factorize n by trial-dividing against a list of sieve primes; O(pi(sqrt(n)))."""
    factors: list[tuple[int, int]] = []
    for prime in sieve_primes:
        if prime * prime > n:
            break
        if n % prime == 0:
            power = 0
            while n % prime == 0:
                n //= prime
                power += 1
            factors.append((prime, power))
    if n > 1:
        factors.append((n, 1))
    return factors


@runner.main
def solve(*args: str) -> str:
    """Count distinct a^b by deduplicating in a set; O(a_max * b_max) insertions dominate.

    Same strategy as s0 but trial-divides only against primesieve-generated
    primes: large bounds key on the prime-factorization signature
    (prime, exponent*b), equal exactly when the powers are equal; small bounds
    key on the exact big-integer value.
    """
    a_min = runner.parse_int(args[0])
    a_max = runner.parse_int(args[1])
    b_min = runner.parse_int(args[2])
    b_max = runner.parse_int(args[3])

    if min(a_max, b_max) > 100:
        sieve_primes = primes(int(a_max**0.5) + 1)
        unique_powers = set()
        for a in range(a_min, a_max + 1):
            prime_factors = factorize(a, sieve_primes)
            for b in range(b_min, b_max + 1):
                signature = tuple(((prime, power * b) for prime, power in prime_factors))
                unique_powers.add(signature)
        return str(len(unique_powers))
    else:
        return str(len({a**b for a in range(a_min, a_max + 1) for b in range(b_min, b_max + 1)}))


if __name__ == "__main__":
    raise SystemExit(solve())
