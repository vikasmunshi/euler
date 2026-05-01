#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0049/p0049.py
  func: solve_prime_permutations_p0049_s0
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, permutations
from sys import argv
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
    n_digit_primes: Set[str] = {str(p) for p in primes_sundaram_sieve(10**n) if p > min_n_digit_hum}
    for prime in n_digit_primes:
        permuted_primes: Set[str] = set((p for d in permutations(prime) if (p := "".join(d)) in n_digit_primes))
        if len(permuted_primes) >= 3:
            differences: Dict[int, Set[str]] = defaultdict(set)
            for prime_i, prime_j in combinations(permuted_primes, 2):
                differences[abs(int(prime_j) - int(prime_i))].update((prime_i, prime_j))
            for difference, primes in differences.items():
                if len(primes) == 3:
                    sequences.add(" ".join(sorted(primes)))
    return sorted(sequences)


def main() -> int:
    print(solve(n=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
