#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 26: Reciprocal Cycles.

  Problem Statement:
    A unit fraction contains 1 in the numerator. The decimal representation of
    the unit fractions with denominators 2 to 10 are given:

    1/2 = 0.5
    1/3 = 0.(3)
    1/4 = 0.25
    1/5 = 0.2
    1/6 = 0.1(6)
    1/7 = 0.(142857)
    1/8 = 0.125
    1/9 = 0.(1)
    1/10 = 0.1

    Where 0.1(6) means 0.166666... and has a 1-digit recurring cycle. It can be
    seen that 1/7 has a 6-digit recurring cycle.

    Find the value of d < 1000 for which 1/d contains the longest recurring cycle
    in its decimal fraction part.

  Solution Approach:
    To solve this problem, investigate the decimal representation of the unit
    fractions 1/d for d less than 1000. The length of the recurring cycle in the
    decimal expansion of 1/d is related to the order of 10 modulo d, which can be
    found using modular arithmetic. By computing the smallest positive integer k
    such that 10^k \equiv 1 (mod d), you determine the cycle length. Iterate over
    all denominators less than 1000 to find the maximum cycle length. Efficient
    implementation might involve skipping numbers with factors 2 and 5 since
    these denominators produce terminating decimals.

  Test Cases:
    preliminary:
      max_val=10,
      answer=7.

    main:
      max_val=100,
      answer=97.

    extended:
      max_val=1000,
      answer=983.

      max_val=10000,
      answer=9967.


  Answer: 97
  URL: https://projecteuler.net/problem=26
"""
from __future__ import annotations

from math import gcd
from typing import Optional

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=26, test_case_category=TestCaseCategory.EXTENDED)
def reciprocal_cycles(*, max_val: int) -> int:
    return max(((multiplicative_order(a=10, modulus=d), d) for i in range(max(max_val // 10, 10)) if
                (d := (max_val - i)) > 6 and gcd(d, 10) == 1))[1]


def multiplicative_order(a: int, modulus: int) -> Optional[int]:
    r = 1
    for k in range(1, modulus):
        r = r * a % modulus
        if r == 1:
            return k
    else:
        return None


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=26, time_out_in_seconds=300, mode='evaluate'))
