#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 1: Multiples Of 3 Or 5.

  Problem Statement:
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we
    get 3, 5, 6, and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.

  Solution Approach:
    To solve this problem, consider using the principle of inclusion and exclusion.
    First, sum all multiples of 3 below the limit, then sum all multiples of 5,
    and subtract the sum of multiples of 15 to avoid double counting. You can use
    arithmetic progression formulas to efficiently calculate these sums without
    iteration. This approach ensures an optimal and clean solution.

  Test Cases:
    preliminary:
      max_limit=10,
      answer=23.

    main:
      max_limit=1000,
      answer=233168.

    extended:
      max_limit=1000000000,
      answer=233333333166666668.


  Answer: 233168
  URL: https://projecteuler.net/problem=1
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.arithmetic_series import generate_arithmetic_series, sum_arithmetic_series
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=1, test_case_category=TestCaseCategory.MAIN)
def multiples_of_3_or_5_series(*, max_limit: int) -> int:
    multiples_of_3 = list(generate_arithmetic_series(d=3, max_num=max_limit - 1))
    multiples_of_5 = list(generate_arithmetic_series(d=5, max_num=max_limit - 1))
    multiples_of_15 = list(generate_arithmetic_series(d=15, max_num=max_limit - 1))
    return sum(multiples_of_3) + sum(multiples_of_5) - sum(multiples_of_15)


@register_solution(euler_problem=1, test_case_category=TestCaseCategory.EXTENDED)
def multiples_of_3_or_5_sum(*, max_limit: int) -> int:
    return (sum_arithmetic_series(first_term=0, common_difference=3, max_limit=max_limit)
            + sum_arithmetic_series(first_term=0, common_difference=5, max_limit=max_limit)
            - sum_arithmetic_series(first_term=0, common_difference=15, max_limit=max_limit))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=1, time_out_in_seconds=300, mode='evaluate'))
