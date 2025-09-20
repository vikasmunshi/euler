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

from euler_solver.framework import evaluate, logger, register_solution
from euler_solver.lib_primes import primes_sundaram_sieve

euler_problem: int = 49
framework_version: str = '0.2.1'
test_cases: list[dict[str, Any]] = [
    {'category': 'main', 'input': {'n': 4}, 'answer': ['1487 4817 8147', '2969 6299 9629']},
    {'category': 'extra', 'input': {'n': 5}, 'answer': ['11483 14813 18143', '11497 41719 71941', '12713 13217 13721',
                                                        '12739 17239 21739', '12757 17257 21757', '12799 17299 21799',
                                                        '14821 48121 81421', '14831 31481 48131', '18503 51803 85103',
                                                        '19543 35491 51439', '20161 20611 21061', '20353 25303 30253',
                                                        '20359 25309 30259', '20747 24077 27407', '23887 28387 32887',
                                                        '25087 52807 80527', '25793 59273 92753', '25981 59281 92581',
                                                        '29669 62969 96269', '31489 34819 38149', '31489 39841 48193',
                                                        '32969 63299 93629', '34961 39461 43961', '35407 40357 45307',
                                                        '35671 53617 71563', '37561 51637 65713', '49547 54497 59447',
                                                        '55603 56053 56503', '60373 63703 67033', '60757 65707 70657',
                                                        '61487 64817 68147', '62597 65927 69257', '62773 67723 72673',
                                                        '63499 63949 64399', '67829 68279 68729', '68713 78163 87613',
                                                        '71947 74719 77491', '73589 78593 83597', '76717 77167 77617',
                                                        '76819 81769 86719', '89387 93887 98387', '92381 92831 93281']},
]


@register_solution(euler_problem=euler_problem, max_test_case_index=None)
def solve_prime_permutations_p0049_s0(*, n: int) -> list:
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
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=euler_problem, time_out_in_seconds=300))
