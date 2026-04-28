#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0051/p0051.py :: solve_prime_digit_replacements_p0051_s0.

Project Euler Problem 51: Prime Digit Replacements.

Problem Statement:
    By replacing the 1st digit of the 2-digit number *3, it turns out that six of the nine
    possible values: 13, 23, 43, 53, 73, and 83, are all prime.

    By replacing the 3rd and 4th digits of 56**3 with the same digit, this 5-digit number is
    the first example having seven primes among the ten generated numbers, yielding the family:
    56003, 56113, 56333, 56443, 56663, 56773, and 56993. Consequently 56003, being the first
    member of this family, is the smallest prime with this property.

    Find the smallest prime which, by replacing part of the number (not necessarily adjacent
    digits) with the same digit, is part of an eight prime value family.

Solution Approach:
    Use prime checking and efficient digit replacement patterns. Generate candidate primes and
    examine digit subsets for replacement to form families. Employ combinatorics on digit indices,
    prime sieves, and incremental search. Aim for pruning by early skips to handle large search
    efficiently.

Answer: 121313
URL: https://projecteuler.net/problem=51"""
from __future__ import annotations


def is_prime(num: int) -> bool:
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


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
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


def solve(*, num_digits: int, prime_run: int) -> int:
    for prime in primes_sundaram_sieve(10 ** num_digits):
        for replaced in '0123456789'[:10 - prime_run]:
            sequence = tuple((new_prime for replacement in '0123456789' if replacement >= replaced if
                              (new_prime := int(str(prime).replace(replaced, replacement))) >= prime and is_prime(
                                  new_prime)))
            if len(sequence) == prime_run:
                return prime
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    import sys

    print(solve(num_digits=int(sys.argv[1]), prime_run=int(sys.argv[2])))
