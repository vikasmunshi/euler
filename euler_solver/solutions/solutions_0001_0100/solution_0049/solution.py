#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
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
URL: https://projecteuler.net/problem=49
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations, permutations
from typing import Any, Dict, Set

from euler_solver.logger import logger
from euler_solver.maths.primes import get_pre_computed_primes_sundaram_sieve
from euler_solver.setup import evaluate, register_solution

euler_problem: int = 49
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 4}},
    {'category': 'extended', 'input': {'n': 5}}
]


@register_solution(euler_problem=euler_problem, max_test_case=None)
def solve_prime_permutations_p0049_s0(*, n: int) -> list:
    sequences: Set[str] = set()
    min_n_digit_hum = 10 ** (n - 1)
    n_digit_primes: Set[str] = {str(p) for p in get_pre_computed_primes_sundaram_sieve(max_limit=10 ** n) if
                                p > min_n_digit_hum}
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
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300, mode='evaluate'))
