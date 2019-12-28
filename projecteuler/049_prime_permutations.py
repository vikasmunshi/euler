#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
https://projecteuler.net/problem=49
The arithmetic sequence, 1487, 4817, 8147, in which each of the terms increases by 3330, is unusual in two ways:
(i) each of the three terms are prime, and, (ii) each of the 4-digit numbers are permutations of one another.

There are no arithmetic sequences made up of three 1-, 2-, or 3-digit primes, exhibiting this property,
but there is one other 4-digit increasing sequence.

What 12-digit number do you form by concatenating the three terms in this sequence?
Answer: 296962999629
"""
from itertools import combinations, permutations
from collections import defaultdict


def solution(n: int) -> {str}:
    sequences = set()
    n_nines = 10 ** n - 1
    sieve = [True] * (n_nines // 2)
    for i in range(3, int(n_nines ** 0.5) + 1, 2):
        if sieve[i // 2]:
            sieve[i * i // 2::i] = [False] * ((n_nines - i * i - 1) // (2 * i) + 1)
    n_digit_primes = set(str(p) for p in [2 * i + 1 for i in range(1, n_nines // 2) if sieve[i]] if p > n_nines // 10)
    for prime in n_digit_primes:
        permuted_primes = set(p for d in permutations(prime) if (p := ''.join(d)) in n_digit_primes)
        if len(permuted_primes) >= 3:
            differences = defaultdict(set)
            for prime_i, prime_j in combinations(permuted_primes, 2):
                differences[abs(int(prime_j) - int(prime_i))].update((prime_i, prime_j))
            for difference, primes in differences.items():
                if len(primes) == 3:
                    sequences.add(' '.join(sorted(primes)))
    return sequences


if __name__ == '__main__':
    from .evaluate import Watchdog

    with Watchdog() as wd:
        results = wd.evaluate_range(solution, answers={4: {'1487 4817 8147', '2969 6299 9629'}, 5: {}})
