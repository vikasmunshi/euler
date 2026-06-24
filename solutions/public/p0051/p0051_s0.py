#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 51: Prime Digit Replacements [Level 2]. """
from __future__ import annotations

from solver.runners import runner


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Primes up to max_num via the Sundaram sieve; index i is composite iff i = a + b + 2ab."""
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
    """Trial division up to sqrt(num), tested per candidate rather than via a second sieve."""
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


@runner.main
def solve(*args: str) -> str:
    """Scan primes ascending; replace one digit value (only 0..9-prime_run can start the family)
    with values from it up to 9, counting forward-only prime members of equal length. Return the
    first prime whose family size reaches prime_run; O(P * D) over P primes below 10^num_digits."""
    num_digits = runner.parse_int(args[0])
    prime_run = runner.parse_int(args[1])

    for prime in primes_sundaram_sieve(10**num_digits):
        for replaced in "0123456789"[: 10 - prime_run]:
            sequence = tuple(
                (
                    new_prime
                    for replacement in "0123456789"
                    if replacement >= replaced
                    if (new_prime := int(str(prime).replace(replaced, replacement))) >= prime and is_prime(new_prime)
                )
            )
            if len(sequence) == prime_run:
                return str(prime)
    else:
        raise ValueError("No solution found")


if __name__ == "__main__":
    raise SystemExit(solve())
