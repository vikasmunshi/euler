#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 72: Counting Fractions.

  Problem Statement:
    Consider the fraction, n over d, where n and d are positive integers. If n is less
    than d and the highest common factor (HCF) of n and d is 1, it is called a reduced
    proper fraction.

    If we list the set of reduced proper fractions for d less than or equal to 8 in
    ascending order of size, we get:
    1 over 8, 1 over 7, 1 over 6, 1 over 5, 1 over 4, 2 over 7, 1 over 3, 3 over 8,
    2 over 5, 3 over 7, 1 over 2, 4 over 7, 3 over 5, 5 over 8, 2 over 3, 5 over 7,
    3 over 4, 4 over 5, 5 over 6, 6 over 7, 7 over 8.

    It can be seen that there are 21 elements in this set.

    How many elements would be contained in the set of reduced proper fractions for d
    less than or equal to 1,000,000?

  Solution Approach:
    To solve this problem, we need to count the number of reduced proper fractions with
    denominators up to a given limit. A key concept is Euler's Totient function phi(d),
    which counts the positive integers up to d that are relatively prime to d.

    The total number of reduced proper fractions for denominators less than or equal to
    N is the sum of phi(d) for d from 2 to N.

    An efficient algorithm involves using a sieve-like method to compute the totient
    values for all numbers up to N. This approach avoids individually checking
    coprimality for each fraction and leverages number-theoretic properties for fast
    computation.

    Implementing this approach with optimized data structures and careful iteration
    will allow the calculation for N = 1,000,000 within a reasonable time frame.

  Test Cases:
    preliminary:
      max_d=8,
      answer=21.

      max_d=10,
      answer=31.

      max_d=100,
      answer=3043.

      max_d=1000,
      answer=304191.

      max_d=10000,
      answer=30397485.

      max_d=100000,
      answer=3039650753.

    main:
      max_d=1000000,
      answer=303963552391.

    extended:
      max_d=10000000,
      answer=30396356427241.


  Answer: 303963552391
  URL: https://projecteuler.net/problem=72
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=72, test_case_category=TestCaseCategory.EXTENDED)
def counting_fractions(*, max_d: int) -> int:
    euler_totients: List[int] = list(range(max_d + 1))
    for n in range(2, max_d + 1):
        if euler_totients[n] == n:
            for j in range(n, max_d + 1, n):
                euler_totients[j] = euler_totients[j] // n * (n - 1)
    return sum((euler_totients[d] for d in range(2, max_d + 1)))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=72, time_out_in_seconds=300, mode='evaluate'))
