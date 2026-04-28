#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0010/p0010.py :: solve_summation_of_primes_p0010_s4_pps.

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

import pyprimesieve as pps


def solve(*, max_num: int) -> int:
    return pps.primes_sum(max_num)  # type: ignore[no-any-return]


if __name__ == '__main__':
    import sys

    print(solve(max_num=int(sys.argv[1])))
