#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0049/p0049.py :: solve_prime_permutations_p0049_s0.

Project Euler Problem 49: Prime Permutations.

Problem Statement:
    The arithmetic sequence, 1487, 4817, 8147, in which each of the terms
    increases by 3330, is unusual in two ways: (i) each of the three terms
    are prime, and, (ii) each of the 4-digit numbers are permutations of
    one another.

    There are no arithmetic sequences made up of three 1-, 2-, or 3-digit
    primes, exhibiting this property, but there is one other 4-digit
    increasing sequence.

    What 12-digit number do you form by concatenating the three terms in
    this sequence?

Solution Approach:
    Search 4-digit primes and find arithmetic sequences with three terms
    that are permutations of each other. Use checks for prime status,
    permutation equality, and arithmetic difference. Efficient prime
    generation and permutation grouping reduce the search space.

Answer: ['1487 4817 8147', '2969 6299 9629']
URL: https://projecteuler.net/problem=49"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations, permutations
from typing import Dict, Set


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


def solve(*, n: int) -> list:
    sequences: Set[str] = set()
    min_n_digit_hum = 10 ** (n - 1)
    n_digit_primes: Set[str] = {str(p) for p in primes_sundaram_sieve(10 ** n) if p > min_n_digit_hum}
    for prime in n_digit_primes:
        permuted_primes: Set[str] = set((p for d in permutations(prime) if (p := ''.join(d)) in n_digit_primes))
        if len(permuted_primes) >= 3:
            differences: Dict[int, Set[str]] = defaultdict(set)
            for prime_i, prime_j in combinations(permuted_primes, 2):
                differences[abs(int(prime_j) - int(prime_i))].update((prime_i, prime_j))
            for difference, primes in differences.items():
                if len(primes) == 3:
                    sequences.add(' '.join(sorted(primes)))
    return sorted(sequences)


if __name__ == '__main__':
    import sys

    print(solve(n=int(sys.argv[1])))
