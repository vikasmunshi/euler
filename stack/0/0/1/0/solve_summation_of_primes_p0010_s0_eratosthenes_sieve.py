#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py

Project Euler Problem 10: Summation of Primes.

Problem Statement:
    The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.

    Find the sum of all the primes below two million.

Solution Approach:
    Use a prime sieve (e.g., Sieve of Eratosthenes) to efficiently find all primes below
    the given limit. Sum these primes. This approach runs in O(n log log n) time and uses
    O(n) space for the sieve.

Answer: 142913828922
URL: https://projecteuler.net/problem=10"""
from __future__ import annotations


def primes_eratosthenes_sieve_upto_max_num(max_num: int) -> tuple[int, ...]:
    if max_num < 2:
        return ()
    sieve = bytearray(b'\x01') * (max_num + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(max_num ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, max_num + 1, i)))
    return tuple((i for i in range(2, max_num + 1) if sieve[i]))


def solve(*, max_num: int) -> int:
    return sum(primes_eratosthenes_sieve_upto_max_num(max_num))


if __name__ == '__main__':
    import sys

    print(solve(max_num=int(sys.argv[1])))
