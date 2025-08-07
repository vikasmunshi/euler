#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 31: Coin Sums.

  Problem Statement:
    In the United Kingdom the currency is made up of pound (\u00a3) and pence (p). There
    are eight coins in general circulation:

    1p, 2p, 5p, 10p, 20p, 50p, \u00a31 (100p), and \u00a32 (200p).

    It is possible to make \u00a32 in the following way:

    1 x \u00a31 + 1 x 50p + 2 x 20p + 1 x 5p + 1 x 2p + 3 x 1p

    How many different ways can \u00a32 be made using any number of coins?

  Solution Approach:
    To solve this problem, consider using dynamic programming to count the number
    of ways to make a total sum using a given set of coin denominations. Begin by
    representing each coin value in pence to work with integers. Then create an
    array where each index represents a sub-amount up to the target (200p).
    Iteratively update this array by adding the ways to form each amount with the
    current coin. This approach efficiently counts combinations without repetitions,
    taking care to handle each coin denomination in sequence to avoid counting
    identical sets multiple times.

  Test Cases:
    preliminary:
      coins=[1, 2, 5, 10, 20, 50, 100, 200],
      target=0,
      answer=1.

    main:
      coins=[1, 2, 5, 10, 20, 50, 100, 200],
      target=200,
      answer=73682.

    extended:
      coins=[1, 2, 5, 10, 20, 50, 100, 200],
      target=1000,
      answer=321335886.

      coins=[1, 2, 5, 10, 20, 50, 100, 200],
      target=100000,
      answer=10056050940818192726001.


  Answer: 73682
  URL: https://projecteuler.net/problem=31
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=31, test_case_category=TestCaseCategory.EXTENDED)
def coin_sums(*, coins: list, target: int) -> int:
    result = [1] + [0] * target
    for coin in coins:
        for i in range(coin, target + 1):
            result[i] += result[i - coin]
    return result[-1]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=31, time_out_in_seconds=300, mode='evaluate'))
