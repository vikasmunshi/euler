#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 48: Self Powers.

  Problem Statement:
    The series, 1 x 1 + 2 x 2 + 3 x 3 + \u22ef + 10 x 10 = 10405071317.

    Find the last ten digits of the series, 1 x 1 + 2 x 2 + 3 x 3 + \u22ef +
    1000 x 1000.

  Solution Approach:
    To solve this problem, consider calculating each term n^n for n from 1
    to 1000, and summing them while keeping track of only the last ten digits.
    This can be efficiently done using modular exponentiation with modulus 10^10,
    which avoids handling very large numbers directly. The approach exploits
    properties of modular arithmetic to maintain manageable number sizes and
    achieve correct last ten digits of the sum.

  Test Cases:
    preliminary:
      n=10,
      answer=405071317.

      n=100,
      answer=9027641920.

    main:
      n=1000,
      answer=9110846700.

    extended:
      n=10000,
      answer=6237204500.

      n=100000,
      answer=3031782500.

      n=1000000,
      answer=4077562500.


  Answer: 9110846700
  URL: https://projecteuler.net/problem=48
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=48, test_case_category=TestCaseCategory.EXTENDED)
def self_powers(*, n: int) -> int:
    modulo: int = 10 ** 10
    result: int = 0
    for i in range(1, n + 1):
        term = pow(i, i, modulo)
        result = (result + term) % modulo
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=48, time_out_in_seconds=300, mode='evaluate'))
