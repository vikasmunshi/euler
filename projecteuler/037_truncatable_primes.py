#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=37
The number 3797 has an interesting property.
Being prime itself, it is possible to continuously remove digits from left to right, and remain prime at each stage:
3797, 797, 97, and 7. Similarly we can work from right to left: 3797, 379, 37, and 3.

Find the sum of the only eleven primes that are both truncatable from left to right and right to left.

NOTE: 2, 3, 5, and 7 are not considered to be truncatable primes.
Answer: 748317
"""
from typing import Generator


def gen_primes_sieve() -> Generator[str, None, None]:
    known_composites = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:
            yield str(current_number)
            known_composites[current_number * current_number] = [current_number]
        else:
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
        current_number += 1


def sum_truncatable_primes() -> int:
    primes = set()
    truncatable_primes = list()
    for prime in gen_primes_sieve():
        primes.add(prime)
        if not any(pl not in primes or pr not in primes
                   for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))]):
            truncatable_primes.append(prime)
        if len(truncatable_primes) == 15:
            break
    return sum(int(p) for p in truncatable_primes if p not in {'2', '3', '5', '7'})


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(sum_truncatable_primes)(answer=748317)
