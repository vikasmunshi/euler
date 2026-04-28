#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0027/p0027.py :: solve_quadratic_primes_p0027_s0.

Project Euler Problem 27: Quadratic Primes.

Problem Statement:
    Euler discovered the remarkable quadratic formula:

        n^2 + n + 41

    It turns out that the formula will produce 40 primes for the consecutive
    integer values 0 <= n <= 39. However, when n = 40, 40^2 + 40 + 41 =
    40(40 + 1) + 41 is divisible by 41, and certainly when n = 41,
    41^2 + 41 + 41 is clearly divisible by 41.

    The incredible formula n^2 - 79n + 1601 was discovered, which produces 80
    primes for the consecutive values 0 <= n <= 79. The product of the
    coefficients, -79 and 1601, is -126479.

    Considering quadratics of the form:

        n^2 + a*n + b, where |a| < 1000 and |b| <= 1000

        where |n| is the modulus/absolute value of n
        e.g. |11| = 11 and |-4| = 4

    Find the product of the coefficients, a and b, for the quadratic
    expression that produces the maximum number of primes for consecutive
    values of n, starting with n = 0.

Solution Approach:
    Use brute force search over all integer coefficients a, b within the
    given ranges |a| < 1000 and |b| <= 1000. For each quadratic expression,
    count consecutive primes generated starting at n=0 using a fast primality
    check (e.g., sieve or Miller-Rabin). Track max length and product a*b.
    Time complexity roughly O(2000*2001*L) where L is max consecutive count.

Answer: -59231
URL: https://projecteuler.net/problem=27"""
from __future__ import annotations


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


def prime_run(a: int, b: int) -> int:
    x = 0
    while is_prime(abs(x ** 2 + a * x + b)):
        x += 1
    return x


def solve(*, max_limit: int) -> int:
    return max([max((prime_run(a, b), a * b), (prime_run(a, -b), -a * b), (prime_run(-a, -b), a * b),
                    (prime_run(-a, b), -a * b)) for b in primes_sundaram_sieve(max_limit) for a in
                range(0 if b == 2 else 1, max_limit, 2)])[1]


if __name__ == '__main__':
    import sys

    print(solve(max_limit=int(sys.argv[1])))
