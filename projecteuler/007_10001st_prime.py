#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=7
By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that the 6th prime is 13.

What is the 10001st prime number?
Answer: 104743
"""
from math import log


def nth_prime_sundaram_sieve(n: int) -> int:
    """https://en.wikipedia.org/wiki/Sieve_of_Sundaram"""
    if n == 1:
        return 2
    max_expected_value = int(n * log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + (2 * i * j)] = 0  # mark n where 2n+1 is not a prime as 0
            except IndexError:
                break
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        result = wd.evaluate_range(nth_prime_sundaram_sieve, answers={6: 13, 10001: 104743})
