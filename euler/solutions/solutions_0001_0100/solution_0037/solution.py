#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 37: Truncatable Primes.

  Problem Statement:
    The number 3797 has an interesting property. Being prime itself, it is
    possible to continuously remove digits from left to right, and remain
    prime at each stage: 3797, 797, 97, and 7. Similarly we can work from
    right to left: 3797, 379, 37, and 3.

    Find the sum of the only eleven primes that are both truncatable from
    left to right and right to left.

    NOTE: 2, 3, 5, and 7 are not considered to be truncatable primes.

  Solution Approach:
    To solve this problem, one should identify primes that remain prime
    when digits are truncated from either the left or the right sides.
    A practical approach involves generating candidate primes and checking
    these truncation properties. Efficient primality testing is crucial,
    and caching computed results can reduce redundant checks.

    Start from small primes and attempt to build larger truncatable
    primes by appending digits, ensuring primality at each truncation.
    Since 2, 3, 5, and 7 are excluded, focus on primes greater than these.

    This exploration can be implemented via iterative or recursive search
    with pruning based on truncation primality criteria until the unique
    eleven truncatable primes are found and their sum calculated.

  Test Cases:
    main:
      answer=748317.


  Answer: 748317
  URL: https://projecteuler.net/problem=37
"""
from __future__ import annotations

from typing import List, Set

from euler.logger import logger
from euler.maths.primes import gen_primes_sieve_eratosthenes
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=37, test_case_category=TestCaseCategory.EXTENDED)
def truncatable_primes() -> int:
    primes: Set[str] = set()
    truncatable_primes: List[int] = list()
    for prime_num in gen_primes_sieve_eratosthenes():
        prime = str(prime_num)
        primes.add(prime)
        if int(prime) < 10:
            continue
        if not any((pl not in primes or pr not in primes for pl, pr in
                    [(prime[i:], prime[:i]) for i in range(1, len(prime))])):
            truncatable_primes.append(prime_num)
        if len(truncatable_primes) == 11:
            break
    return sum(truncatable_primes)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=37, time_out_in_seconds=300, mode='evaluate'))
