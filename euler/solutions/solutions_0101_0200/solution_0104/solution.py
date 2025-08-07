#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 104: Pandigital Fibonacci Ends.

  Problem Statement:
    The Fibonacci sequence is defined by the recurrence relation:

    F_n = F_{n - 1} + F_{n - 2}, where F_1 = 1 and F_2 = 1.

    It turns out that F_541, which contains 113 digits, is the first Fibonacci number
    for which the last nine digits are 1-9 pandigital (contain all the digits 1 to 9,
    but not necessarily in order). And F_2749, which contains 575 digits, is the
    first Fibonacci number for which the first nine digits are 1-9 pandigital.

    Given that F_k is the first Fibonacci number for which the first nine digits AND
    the last nine digits are 1-9 pandigital, find k.

  Solution Approach:
    To solve this problem, one should generate Fibonacci numbers and efficiently
    check their digit patterns. Since the numbers grow very large, directly
    computing the full Fibonacci numbers for high indices is computationally
    expensive. Instead, use modular arithmetic to track the last nine digits and
    logarithmic properties or floating-point arithmetic to approximate the first
    nine digits.

    By maintaining the last nine digits modulo 10^9, you can check for pandigitality
    at the end. For the first nine digits, use the fact that the number of digits
    and leading digits can be derived from the logarithm (base 10) of the Fibonacci
    number. Implement a check for pandigitality for both ends and iterate until
    finding the first Fibonacci number where both criteria are met.

  Test Cases:
    main:
      answer=None.


  Answer: None
  URL: https://projecteuler.net/problem=104
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=104, test_case_category=TestCaseCategory.EXTENDED)
def pandigital_fibonacci_ends() -> int:
    raise NotImplementedError()


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=104, time_out_in_seconds=300, mode='evaluate'))
