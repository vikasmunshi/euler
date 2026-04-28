#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0035/p0035.py :: solve_circular_primes_p0035_s1_pps.

Project Euler Problem 35: Circular Primes.

Problem Statement:
    The number, 197, is called a circular prime because all rotations of the digits:
    197, 971, and 719, are themselves prime.

    There are thirteen such primes below 100: 2, 3, 5, 7, 11, 13, 17, 31, 37, 71,
    73, 79, and 97.

    How many circular primes are there below one million?

Solution Approach:
    Use number theory and prime checking with a sieve (e.g., Sieve of Eratosthenes)
    to identify primes below one million. For each prime, generate all digit rotations
    and verify all are prime. Count those where all rotations are prime.

Answer: 55
URL: https://projecteuler.net/problem=35"""
from __future__ import annotations

import bisect
from typing import Set

import pyprimesieve as pps


def get_primes_from_pps(max_limit: int) -> list[int]:
    all_primes = pps.primes(max(max_limit, 10 ** 6))
    return all_primes[:bisect.bisect_right(all_primes, max_limit)]  # type: ignore[no-any-return]


def get_rotated_numbers(*, num: int) -> Set[int]:
    str_num: str = str(num)
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


def solve(*, max_limit: int) -> int:
    primes = set(get_primes_from_pps(max_limit))
    circular_primes = [prime for prime in primes if prime < 10 or (not any((d in str(prime) for d in '024568')) and (
        not any((rotated_number not in primes for rotated_number in get_rotated_numbers(num=prime)))))]
    return len(circular_primes)


if __name__ == '__main__':
    import sys

    print(solve(max_limit=int(sys.argv[1])))
