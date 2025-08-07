#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 50: Consecutive Prime Sum.

  Problem Statement:
    The prime 41 can be written as the sum of six consecutive primes:
    41 = 2 + 3 + 5 + 7 + 11 + 13.

    This is the longest sum of consecutive primes that adds to a prime
    below one-hundred.

    The longest sum of consecutive primes below one-thousand that adds to a
    prime, contains 21 terms, and is equal to 953.

    Which prime, below one-million, can be written as the sum of the most
    consecutive primes?

  Solution Approach:
    To solve this problem, first generate a list of prime numbers up to one
    million using an efficient method such as the Sieve of Eratosthenes.
    Then, explore sums of consecutive primes from this list, keeping track
    of sums that result in a prime number under one million. Focus on
    identifying the longest such sequence. Using cumulative sums can optimize
    the process by allowing rapid calculation of sums over intervals. This
    approach blends number theory and algorithmic optimization techniques.

  Test Cases:
    preliminary:
      max_limit=100,
      answer=41.

      max_limit=1000,
      answer=953.

      max_limit=10000,
      answer=9521.

      max_limit=100000,
      answer=92951.

    main:
      max_limit=1000000,
      answer=997651.


  Answer: 997651
  URL: https://projecteuler.net/problem=50
"""
from __future__ import annotations

from itertools import accumulate
from typing import List, Set, Tuple

from euler.logger import logger
from euler.maths.primes import get_pre_computed_primes_sundaram_sieve
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=50, test_case_category=TestCaseCategory.EXTENDED)
def consecutive_prime_sum(*, max_limit: int) -> int:
    primes_tuple: Tuple[int, ...] = get_pre_computed_primes_sundaram_sieve(max_limit=max_limit)
    prime_sums: List[int] = [0] + list(accumulate(primes_tuple))
    primes: Set[int] = set(primes_tuple)
    number_of_primes_in_sum, prime = (0, 0)
    for i in range(number_of_primes_in_sum, len(prime_sums), 1):
        for j in range(i - number_of_primes_in_sum - 1, -1, -1):
            possible_prime = prime_sums[i] - prime_sums[j]
            if possible_prime > max_limit:
                break
            if possible_prime in primes:
                number_of_primes_in_sum = i - j
                prime = possible_prime
    return prime


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=50, time_out_in_seconds=300, mode='evaluate'))
