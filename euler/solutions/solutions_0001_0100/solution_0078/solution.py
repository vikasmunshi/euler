#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 78: Coin Partitions.

  Problem Statement:
    Let p(n) represent the number of different ways in which n coins can be
    separated into piles. For example, five coins can be separated into piles
    in exactly seven different ways, so p(5) = 7.

        OOOOO
        OOOO   O
        OOO   OO
        OOO   O   O
        OO   OO   O
        OO   O   O   O
        O   O   O   O   O

    Find the least value of n for which p(n) is divisible by one million.

  Solution Approach:
    This problem deals with integer partitions, specifically the number of ways
    to partition an integer n into sums, which corresponds to the piles of coins.
    A classical approach involves generating functions or dynamic programming to
    compute the partition function p(n).

    One effective method is to use the recurrence based on the pentagonal number
    theorem to efficiently compute p(n) modulo one million, checking for the
    smallest n where p(n) % 1,000,000 == 0.

    This approach requires implementing the partition function with memoization
    or tabulation to handle large values of n without excessive computation.

    Understanding modular arithmetic and efficient summation of partition terms
    is key to solving this within a reasonable time frame.

  Test Cases:
    preliminary:
      divisor=1000,
      answer=449.

    main:
      divisor=1000000,
      answer=55374.


  Answer: 55374
  URL: https://projecteuler.net/problem=78
"""
from __future__ import annotations

from itertools import count

from euler.logger import logger
from euler.maths.integer_partitions import num_partitions
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=78, test_case_category=TestCaseCategory.EXTENDED)
def coin_partitions(*, divisor: int) -> int:
    for n in count(2):
        if num_partitions(number=n) % divisor == 0:
            return n
    return -1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=78, time_out_in_seconds=300, mode='evaluate'))
