#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=41
We shall say that an n-digit number is pandigital if it makes use of all the digits 1 to n exactly once.
For example, 2143 is a 4-digit pandigital and is also prime.

What is the largest n-digit pandigital prime that exists?
Answer: 7652413
"""
from itertools import permutations


def is_prime(n: int) -> bool:
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def largest_pandigital_prime() -> int:
    pandigital_primes = (
        number
        for length in (7, 4)
        # all other length pandigital numbers are divisible by 3 {2: 3, 3: 6, 4: 10, 5: 15, 6: 21, 7: 28, 8: 36, 9: 45}
        for number in (int(''.join(digits)) for digits in permutations(reversed('123456789'[:length]), length))
        if is_prime(number)
    )
    return next(pandigital_primes)


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate(largest_pandigital_prime)(answer=7652413)
