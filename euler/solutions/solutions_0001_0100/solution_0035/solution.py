#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 35: Circular Primes.

  Problem Statement:
    The number, 197, is called a circular prime because all rotations of the
    digits: 197, 971, and 719, are themselves prime.

    There are thirteen such primes below 100: 2, 3, 5, 7, 11, 13, 17, 31, 37,
    71, 73, 79, and 97.

    How many circular primes are there below one million?

  Solution Approach:
    To solve the problem of finding circular primes below one million,
    first generate all prime numbers up to that limit using an efficient
    method such as the Sieve of Eratosthenes. Then, for each prime, generate
    all rotations of its digits and check if all these rotations are also
    prime. Count only those primes for which every rotation is prime. Pay
    special attention to digit rotations that may introduce leading zeros or
    change the length of numbers. This approach involves prime testing and
    careful handling of digit manipulations to identify circular primes.

  Test Cases:
    preliminary:
      max_limit=10,
      answer=4.

      max_limit=100,
      answer=13.

      max_limit=1000,
      answer=25.

    main:
      max_limit=1000000,
      answer=55.

    extended:
      max_limit=10000000,
      answer=55.


  Answer: 55
  URL: https://projecteuler.net/problem=35
"""
from __future__ import annotations

from typing import Set

from euler.logger import logger
from euler.maths.primes import get_pre_computed_primes_sundaram_sieve
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=35, test_case_category=TestCaseCategory.EXTENDED)
def circular_primes(*, max_limit: int) -> int:
    primes = set(get_pre_computed_primes_sundaram_sieve(max_limit=max_limit))
    circular_primes = [prime for prime in primes if prime < 10 or (not any((d in str(prime) for d in '024568')) and (
        not any((rotated_number not in primes for rotated_number in get_rotated_numbers(num=prime)))))]
    return len(circular_primes)


def get_rotated_numbers(*, num: int) -> Set[int]:
    str_num: str = str(num)
    return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=35, time_out_in_seconds=300, mode='evaluate'))
