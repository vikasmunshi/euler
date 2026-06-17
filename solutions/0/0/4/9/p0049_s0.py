#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
""" Solution to Euler Problem 49: Prime Permutations [Level 1]. """
from __future__ import annotations

import collections
import itertools

from solver.runners import runner


def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    """Return all primes below max_num via Sundaram's sieve (marks k = i + j + 2ij, prime = 2k+1)."""
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


@runner.main
def solve(*args: str) -> str:
    """Group n-digit primes by permutation siblings, then bucket pairwise differences to find
    arithmetic triples; O(P * n!) permutation work plus O(|family|^2) per family. A bucket holding
    exactly three values is an arithmetic progression with that common difference."""
    n = runner.parse_int(args[0])

    sequences: set[str] = set()
    min_n_digit_hum = 10 ** (n - 1)
    n_digit_primes: set[str] = {str(p) for p in primes_sundaram_sieve(10**n) if p > min_n_digit_hum}
    for prime in n_digit_primes:
        permuted_primes: set[str] = set(
            (p for d in itertools.permutations(prime) if (p := "".join(d)) in n_digit_primes)
        )
        if len(permuted_primes) >= 3:
            differences: dict[int, set[str]] = collections.defaultdict(set)
            for prime_i, prime_j in itertools.combinations(permuted_primes, 2):
                differences[abs(int(prime_j) - int(prime_i))].update((prime_i, prime_j))
            for difference, primes in differences.items():
                if len(primes) == 3:
                    sequences.add(" ".join(sorted(primes)))
    return str(sorted(sequences))


if __name__ == "__main__":
    raise SystemExit(solve())
