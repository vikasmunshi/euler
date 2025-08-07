#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 53: Combinatoric Selections.

  Problem Statement:
    There are exactly ten ways of selecting three from five, 12345:

    123, 124, 125, 134, 135, 145, 234, 235, 245, and 345

    In combinatorics, we use the notation, (5 3) = 10.

    In general, (n r) = n! / (r! (n - r)!), where r \u2264 n, n! = n x (n - 1) x ... x 3
    x 2 x 1, and 0! = 1.

    It is not until n = 23, that a value exceeds one-million: (23 10) = 1144066.

    How many, not necessarily distinct, values of (n r) for 1 \u2264 n \u2264 100,
    are greater than one-million?

  Solution Approach:
    To solve this problem, you need to efficiently calculate binomial coefficients,
    which are given by n! / (r! (n - r)!). However, computing full factorials for
    large n can be expensive. Use properties of binomial coefficients such as symmetry
    (C(n, r) = C(n, n-r)) and iterative formulae to compute values without overflow.

    Iterate through all values of n from 1 to 100 and for each n, iterate through
    values of r from 1 to n. For each combination, check if the binomial coefficient
    exceeds one million. Keep a count of such occurrences.

    Efficient approaches avoid computing factorials repeatedly by using dynamic
    programming or Pascal's triangle relationships. You can also use direct
    multiplicative formulas that build coefficients from previous values.

    This approach balances computational efficiency with clarity to find the count
    of large binomial coefficients within the defined range.

  Test Cases:
    preliminary:
      max_n=100,
      threshold=100,
      answer=4724.

    main:
      max_n=100,
      threshold=1000000,
      answer=4075.

    extended:
      max_n=1000,
      threshold=1000000,
      answer=494861.

      max_n=1000,
      threshold=1000000000,
      answer=491894.


  Answer: 4075
  URL: https://projecteuler.net/problem=53
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=53, test_case_category=TestCaseCategory.EXTENDED)
def combinatoric_selections(*, max_n: int, threshold: int) -> int:
    count = 0
    for n in range(1, max_n + 1):
        c = 1
        for r in range(0, n // 2 + 1):
            if c > threshold:
                count += n - 2 * r + 1
                break
            else:
                c = c * (n - r) // (r + 1)
    return count


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=53, time_out_in_seconds=300, mode='evaluate'))
