#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=51
By replacing the 1st digit of the 2-digit number *3, it turns out that six of the nine possible values:
13, 23, 43, 53, 73, and 83, are all prime.

By replacing the 3rd and 4th digits of 56**3 with the same digit, this 5-digit number is the first example having
seven primes among the ten generated numbers, yielding the family: 56003, 56113, 56333, 56443, 56663, 56773, and 56993.
Consequently 56003, being the first member of this family, is the smallest prime with this property.

Find the smallest prime which, by replacing part of the number (not necessarily adjacent digits) with the same digit,
is part of an eight prime value family.
Answer: 121313
"""


def solution(prime_run: int, num_digits: int = 6) -> int:
    max_val = 10 ** num_digits - 1
    sundaram_sieve = [True] * (max_val // 2)
    for i in range(3, int(max_val ** 0.5) + 1, 2):
        if sundaram_sieve[i // 2]:
            sundaram_sieve[i * i // 2::i] = [False] * ((max_val - i * i - 1) // (2 * i) + 1)
    primes = (2,) + tuple(2 * i + 1 for i in range(1, max_val // 2) if sundaram_sieve[i])
    primes_set = set(primes)

    for prime in primes:
        for replaced in '0123456789'[:10 - prime_run]:
            sequence = tuple(new_prime for replacement in '0123456789' if replacement >= replaced
                             if (new_prime := int(str(prime).replace(replaced, replacement))) >= prime
                             and new_prime in primes_set)
            if len(sequence) == prime_run:
                return prime


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        wd.evaluate_range(solution, answers={6: 13, 7: 56003, 8: 121313})
