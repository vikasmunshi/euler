#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=46
It was proposed by Christian Goldbach that every odd composite number can be written as the
sum of a prime and twice a square.

9 = 7 + 2×1^2
15 = 7 + 2×2^2
21 = 3 + 2×3^2
25 = 7 + 2×3^2
27 = 19 + 2×2^2
33 = 31 + 2×1^2

It turns out that the conjecture was false.

What is the smallest odd composite that cannot be written as the sum of a prime and twice a square?
Answer: 5777
"""


def solution() -> int:
    primes, known_composites = set(), dict()
    current_number = 1
    while current_number := current_number + 1:
        if current_number not in known_composites:  # is a new prime
            primes.add(current_number)
            known_composites[current_number * current_number] = [current_number]  # Eratosthene's seive
        else:
            if current_number % 2 != 0:  # is odd composite
                # check half of current number minus all smaller prime is a perfect square
                if not any((((current_number - p) / 2) ** 0.5) % 1 == 0 for p in primes if current_number > p != 2):
                    return current_number
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(solution)(answer=5777)
