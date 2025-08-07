#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 73: Counting Fractions In A Range.

  Problem Statement:
    Consider the fraction, n\d, where n and d are positive integers. If n < d and
    HCF(n, d) = 1, it is called a reduced proper fraction.

    If we list the set of reduced proper fractions for d <= 8 in ascending order of
    size, we get:
    1\8, 1\7, 1\6, 1\5, 1\4, 2\7, 1\3, 3\8, 2\5, 3\7, 1\2, 4\7, 3\5, 5\8,
    2\3, 5\7, 3\4, 4\5, 5\6, 6\7, 7\8

    It can be seen that there are 3 fractions between 1\3 and 1\2.

    How many fractions lie between 1\3 and 1\2 in the sorted set of reduced proper
    fractions for d <= 12,000?

  Solution Approach:
    To solve this problem, one can use the concept of Farey sequences, which are
    the ascending sequences of reduced fractions between 0 and 1 with denominators
    limited by a certain value. In particular, the problem asks for the count of
    fractions between 1/3 and 1/2 for denominators up to 12,000.

    One approach is to efficiently generate or count the fractions in the Farey
    sequence of order 12,000 that lie between these two fractions. Directly
    enumerating all fractions is computationally expensive due to the large
    limit. Instead, an efficient recursive or iterative method inspired by the
    Farey sequence properties or the Stern-Brocot tree can be applied.

    The method involves counting fractions between two fractions by constructing
    mediants (the fraction formed by summing numerators and denominators of the
    bounding fractions) and recursively counting sub-intervals, stopping when
    denominators exceed the limit. This approach avoids generating all fractions
    explicitly, enabling a feasible solution for large denominators.

  Test Cases:
    preliminary:
      max_d=8,
      answer=3.

      max_d=1000,
      answer=50695.

    main:
      max_d=12000,
      answer=7295372.

    extended:
      max_d=100000,
      answer=506608484.


  Answer: 7295372
  URL: https://projecteuler.net/problem=73
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.sys_utils import set_resource_limits


@register_solution(euler_problem=73, test_case_category=TestCaseCategory.PRELIMINARY)
def counting_fractions_in_a_range_iteration(*, max_d: int) -> int:
    lower_denominator: int = 3
    upper_denominator: int = 2
    d = upper_denominator + lower_denominator * ((max_d - upper_denominator) // lower_denominator)
    prev_d = lower_denominator
    count = 0
    while d != upper_denominator:
        count += 1
        prev_d, d = (d, max_d - (max_d + prev_d) % d)
    return count


@register_solution(euler_problem=73, test_case_category=TestCaseCategory.PRELIMINARY)
@set_resource_limits(recursion_var='max_d', multiplier=1, set_int_max_str=False, when='always')
def counting_fractions_in_a_range_recursion(*, max_d: int) -> int:
    def recursion(lower_denominator: int, upper_denominator: int) -> int:
        if (mediant := (lower_denominator + upper_denominator)) > max_d:
            return 0
        return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)

    return recursion(lower_denominator=3, upper_denominator=2)


@register_solution(euler_problem=73, test_case_category=TestCaseCategory.EXTENDED)
def counting_fractions_in_a_range_rank(*, max_d: int) -> int:
    def rank(n: int, d: int) -> int:
        len_data: int = max_d + 1
        data: List[int] = [i * n // d for i in range(len_data)]
        for i in range(1, len_data):
            for j in range(2 * i, len_data, i):
                data[j] -= data[i]
        return sum(data)

    return rank(n=1, d=2) - rank(n=1, d=3) - 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=73, time_out_in_seconds=300, mode='evaluate'))
