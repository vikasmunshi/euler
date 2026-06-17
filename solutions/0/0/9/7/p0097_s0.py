#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 97: Large Non-Mersenne Prime [Level 1]. """
from __future__ import annotations

from solver.runners import runner


def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    """Evaluate (coeff * 2^exp + 1) mod 10^num_digits to get the last num_digits
    digits; the loop here doubles modulo divisor exp times, so it is O(exp)."""
    divisor: int = 10**num_digits
    prime_parts: list[str] = prime.split()
    number: int
    exponent: int
    number, exponent = (int(prime_parts[0]), int(prime_parts[2][2:]))
    for _ in range(exponent):
        number *= 2
        number %= divisor
    number += 1
    number %= divisor
    return number


@runner.main
def solve(*args: str) -> str:
    """Parse the digit count and prime expression, then return the last
    num_digits digits via modular reduction; O(exp) from the doubling loop."""
    num_digits = runner.parse_int(args[0])
    prime = args[1]

    return str(large_non_mersenne_prime(num_digits=num_digits, prime=prime))


if __name__ == "__main__":
    raise SystemExit(solve())
