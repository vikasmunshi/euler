#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 10: Summation Of Primes.

  Problem Statement:
    The sum of the primes below 10 is 2 + 3 + 5 + 7 = 17.

    Find the sum of all the primes below two million.

  Solution Approach:
    To solve this problem, one can utilize an efficient prime number
    generation technique such as the Sieve of Eratosthenes. This algorithm
    iteratively marks the multiples of each prime starting from 2, allowing
    identification of all primes below a given limit. Once the primes below
    two million are identified, their sum can be computed. Consider using
    optimized data structures or segmented sieves to handle the large
    upper bound efficiently while managing memory usage.

  Test Cases:
    preliminary:
      max_num=10,
      answer=17.

    main:
      max_num=2000000,
      answer=142913828922.

    extended:
      max_num=10000000,
      answer=3203324994356.


  Answer: 142913828922
  URL: https://projecteuler.net/problem=10
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.primes import gen_primes_sieve_eratosthenes, get_pre_computed_primes_sundaram_sieve
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=10, test_case_category=TestCaseCategory.EXTENDED)
def summation_of_primes_sundaram_sieve(*, max_num: int) -> int:
    return sum(get_pre_computed_primes_sundaram_sieve(max_limit=max_num))


@register_solution(euler_problem=10, test_case_category=TestCaseCategory.EXTENDED)
def summation_of_primes_eratosthenes_sieve(*, max_num: int) -> int:
    prime_number_gen = gen_primes_sieve_eratosthenes()
    result: int = 0
    while (prime_number := next(prime_number_gen)) < max_num:
        result += prime_number
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=10, time_out_in_seconds=300, mode='evaluate'))
