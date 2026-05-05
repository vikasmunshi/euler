#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Pure Python implementations of prime number related functions for standalone implementations."""
from __future__ import annotations

from typing import Generator


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


def fast_is_prime(num: int) -> bool:
    return is_prime(num)


def primes_eratosthenes_sieve_upto_max_num(max_num: int) -> tuple[int, ...]:
    if max_num < 2:
        return ()
    sieve = bytearray(b'\x01') * (max_num + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(max_num ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, max_num + 1, i)))
    return tuple(i for i in range(2, max_num + 1) if sieve[i])


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
    primes.extend(2 * i + 1 for i in range(1, n + 1) if not marked[i])
    return tuple(primes)


def primes_generator() -> Generator[int, None, None]:
    yield 2
    composites: dict[int, int] = {}
    n = 3
    while True:
        if n not in composites:
            yield n
            composites[n * n] = n
        else:
            p = composites.pop(n)
            m = n + 2 * p
            while m in composites:
                m += 2 * p
            composites[m] = p
        n += 2


def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
    if n <= 1:
        return ()
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                n //= d
                exp += 1
            factors.append((d, exp))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return tuple(factors)


def num_factors(n: int) -> int:
    if n == 0:
        return 0
    result = 1
    for _, exp in prime_factorization(n):
        result *= exp + 1
    return result


def sum_proper_divisors(n: int) -> int:
    if n <= 1:
        return 0
    result = 1
    i = 2
    while i * i <= n:
        if n % i == 0:
            result += i
            if i != n // i:
                result += n // i
        i += 1
    return result


def prime_factor_count(n: int) -> int:
    return len(prime_factorization(n))
