#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 76: Counting Summations.

  Problem Statement:
    It is possible to write five as a sum in exactly six different ways:

    4 + 1
    3 + 2
    3 + 1 + 1
    2 + 2 + 1
    2 + 1 + 1 + 1
    1 + 1 + 1 + 1 + 1

    How many different ways can one hundred be written as a sum of at least
    two positive integers?

  Solution Approach:
    This problem involves counting the number of integer partitions of a
    given number, where order does not matter and each partition has at
    least two parts. A suitable approach is to use dynamic programming to
    build the count of partitions incrementally. Define a function to
    represent the number of ways to write an integer as a sum of smaller
    integers, considering constraints to avoid counting duplicates.

    Efficient implementation stores intermediate results in a table to
    avoid redundant calculations. Familiarity with partition theory and
    combinatorics is helpful to understand the problem's mathematical
    foundations. The goal is to compute the total number of partitions of
    100 with at least two positive integers.

  Test Cases:
    preliminary:
      num=5,
      answer=6.

      num=50,
      answer=204225.

    main:
      num=100,
      answer=190569291.

    extended:
      num=1000,
      answer=24061467864032622473692149727990.


  Answer: 190569291
  URL: https://projecteuler.net/problem=76
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.integer_partitions import get_partitions, num_integer_partitions, num_partitions
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.sys_utils import set_resource_limits


@register_solution(euler_problem=76, test_case_category=TestCaseCategory.PRELIMINARY)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def counting_summations_recursion(*, num: int) -> int:
    return num_integer_partitions(number=num, slots=num) - 1


@register_solution(euler_problem=76, test_case_category=TestCaseCategory.PRELIMINARY)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def counting_summations_listing_partitions(*, num: int) -> int:
    return len(get_partitions(number=num, slots=num)) - 1


@register_solution(euler_problem=76, test_case_category=TestCaseCategory.EXTENDED)
@set_resource_limits(recursion_var='num', multiplier=2, set_int_max_str=False, when='always')
def counting_summations_formula(*, num: int) -> int:
    return num_partitions(number=num) - 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=76, time_out_in_seconds=300, mode='evaluate'))
