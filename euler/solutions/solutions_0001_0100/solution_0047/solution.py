#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 47: Distinct Primes Factors.

  Problem Statement:
    The first two consecutive numbers to have two distinct prime factors are:

    14 = 2 x 7
    15 = 3 x 5.

    The first three consecutive numbers to have three distinct prime factors are:

    644 = 2^2 x 7 x 23
    645 = 3 x 5 x 43
    646 = 2 x 17 x 19.

    Find the first four consecutive integers to have four distinct prime factors
    each. What is the first of these numbers?

  Solution Approach:
    To solve this problem, iteratively examine consecutive integers and determine
    the count of distinct prime factors for each. Efficiently factor numbers using
    precomputed primes or a sieve method. Once finding four consecutive numbers with
    exactly four distinct prime prime factors, identify and return the first. This
    approach benefits from efficient factorization algorithms and careful iteration
    through integers.

  Test Cases:
    preliminary:
      n=2,
      answer=14.

      n=3,
      answer=644.

    main:
      n=4,
      answer=134043.


  Answer: 134043
  URL: https://projecteuler.net/problem=47
"""
from __future__ import annotations

from itertools import count

from euler.logger import logger
from euler.maths.primes import prime_factor_count
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=47, test_case_category=TestCaseCategory.EXTENDED)
def distinct_primes_factors(*, n: int) -> int:
    return next((number for number in count(2) if not any((prime_factor_count(number + i) != n for i in range(0, n)))))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=47, time_out_in_seconds=300, mode='evaluate'))
