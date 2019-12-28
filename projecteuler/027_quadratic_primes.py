#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=27
Euler discovered the remarkable quadratic formula:
n^2+n+41
It turns out that the formula will produce 40 primes for the consecutive integer values 0≤n≤39.
However, when n=40,40^2+40+41=40(40+1)+41 is divisible by 41,
and certainly when n=41,41^2+41+41 is clearly divisible by 41.

The incredible formula n^2−79n+1601 was discovered, which produces 80 primes for the consecutive values 0≤n≤79.
The product of the coefficients, −79 and 1601, is −126479.

Considering quadratics of the form:
n^2+an+b, where |a|<1000 and |b|≤1000

where |n| is the modulus/absolute value of n
e.g. |11|=11 and |−4|=4
Find the product of the coefficients, a and b, for the quadratic expression that produces the maximum number of primes
for consecutive values of n, starting with n=0.
Answer: -59231
"""
from functools import lru_cache


def gen_primes_sundaram_sieve(max_limit: int) -> (int, ...):
    if max_limit < 2:
        return 2,
    max_number = (max_limit - 1) // 2 + 1
    numbers = list(range(0, max_number))
    for i in numbers[1:]:
        for j in range(i, max_number):
            try:
                numbers[i + j + (2 * i * j)] = 0  # mark n where 2n+1 is not a prime as 0
            except IndexError:
                break
    return (2,) + tuple(2 * i + 1 for i in numbers if i != 0)


@lru_cache(maxsize=None)
def is_prime(n: int) -> bool:
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def prime_run(a: int, b: int) -> int:
    x = 0
    while is_prime(abs(x ** 2 + a * x + b)):
        x += 1
    return x + 1


def longest_quadratic_primes(max_limit: int) -> int:
    return max([
        max((prime_run(a, b), a * b),
            (prime_run(a, -b), -a * b),
            (prime_run(-a, -b), a * b),
            (prime_run(-a, b), -a * b))
        for b in gen_primes_sundaram_sieve(max_limit)
        for a in range(0 if b == 2 else 1, max_limit, 2)
    ])[1]


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(longest_quadratic_primes, answers={1000: -59231})
