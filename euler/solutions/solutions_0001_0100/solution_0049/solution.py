#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 49: Prime Permutations.

  Problem Statement:
    The arithmetic sequence, 1487, 4817, 8147, in which each of the terms
    increases by 3330, is unusual in two ways: (i) each of the three terms are
    prime, and, (ii) each of the 4-digit numbers are permutations of one
    another.

    There are no arithmetic sequences made up of three 1-, 2-, or 3-digit
    primes, exhibiting this property, but there is one other 4-digit increasing
    sequence.

    What 12-digit number do you form by concatenating the three terms in this
    sequence?

  Solution Approach:
    To solve this problem, start by generating all 4-digit prime numbers.
    Then, group these primes by their digit permutations, identifying sets
    of primes that are permutations of each other.

    For each such group, search for sequences of three primes that form an
    arithmetic progression, i.e., the difference between consecutive terms
    is constant.

    Finally, concatenate the three terms of the found sequence to form the
    required 12-digit number. Efficient prime generation, permutation
    checking, and arithmetic sequence detection are key components.

  Test Cases:
    main:
      n=4,
      answer=['1487 4817 8147', '2969 6299 9629'].

    extended:
      n=5,
      answer=['11483 14813 18143', '11497 41719 71941', '12713 13217 13721', '12
             739 17239 21739', '12757 17257 21757', '12799 17299 21799', '14821
             48121 81421', '14831 31481 48131', '18503 51803 85103', '19543 3549
             1 51439', '20161 20611 21061', '20353 25303 30253', '20359 25309 30
             259', '20747 24077 27407', '23887 28387 32887', '25087 52807 80527'
             , '25793 59273 92753', '25981 59281 92581', '29669 62969 96269', '3
             1489 34819 38149', '31489 39841 48193', '32969 63299 93629', '34961
              39461 43961', '35407 40357 45307', '35671 53617 71563', '37561 516
             37 65713', '49547 54497 59447', '55603 56053 56503', '60373 63703 6
             7033', '60757 65707 70657', '61487 64817 68147', '62597 65927 69257
             ', '62773 67723 72673', '63499 63949 64399', '67829 68279 68729', '
             68713 78163 87613', '71947 74719 77491', '73589 78593 83597', '7671
             7 77167 77617', '76819 81769 86719', '89387 93887 98387', '92381 92
             831 93281'].


  Answer: ['1487 4817 8147', '2969 6299 9629']
  URL: https://projecteuler.net/problem=49
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations, permutations
from typing import Dict, Set

from euler.logger import logger
from euler.maths.primes import get_pre_computed_primes_sundaram_sieve
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=49, test_case_category=TestCaseCategory.EXTENDED)
def prime_permutations(*, n: int) -> list:
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
    raise SystemExit(evaluate(euler_problem=49, time_out_in_seconds=300, mode='evaluate'))
