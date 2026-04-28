#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0097/p0097.py :: solve_large_non_mersenne_prime_p0097_s0.

Project Euler Problem 97: Large Non-Mersenne Prime.

Problem Statement:
    The first known prime found to exceed one million digits was discovered in 1999,
    and is a Mersenne prime of the form 2^6972593 - 1; it contains exactly 2098960 digits.
    Subsequently other Mersenne primes, of the form 2^p - 1, have been found which contain
    more digits.

    However, in 2004 there was found a massive non-Mersenne prime which contains 2357207 digits:
    28433 * 2^7830457 + 1.

    Find the last ten digits of this prime number.

Solution Approach:
    Use modular arithmetic to compute (28433 * 2^7830457 + 1) mod 10^10 efficiently.
    Employ fast exponentiation (binary exponentiation) for O(log n) complexity in exponentiation.
    This avoids handling the entire large number outright.

Answer: 8739992577
URL: https://projecteuler.net/problem=97"""
from __future__ import annotations


def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    divisor: int = 10 ** num_digits
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


def solve(*, num_digits: int, prime: str) -> int:
    return large_non_mersenne_prime(num_digits=num_digits, prime=prime)


if __name__ == '__main__':
    import sys

    print(solve(num_digits=int(sys.argv[1]), prime=str(sys.argv[2])))
