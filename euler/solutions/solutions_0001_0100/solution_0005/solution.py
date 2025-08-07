#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 5: Smallest Multiple.

  Problem Statement:
    2520 is the smallest number that can be divided by each of the numbers
    from 1 to 10 without any remainder.

    What is the smallest positive number that is evenly divisible by all of
    the numbers from 1 to 20?

  Solution Approach:
    To solve this problem, focus on the concept of the Least Common Multiple
    (LCM). The smallest number divisible by all numbers in a range is the
    LCM of those numbers.

    A practical approach is to compute the LCM of all integers from 1 to 20.
    This can be done efficiently by iteratively calculating the LCM of the
    current number with the running result.

    The LCM of two numbers a and b can be found using their Greatest Common
    Divisor (GCD) with the formula: LCM(a,b) = abs(a*b) / GCD(a,b).

    Implement an algorithm that uses the Euclidean method for GCD computation
    and then uses it to calculate the LCM for the sequence 1 to 20.

    This reduces the problem to a sequence of simple arithmetic operations,
    making the solution computationally efficient.

  Test Cases:
    preliminary:
      n=10,
      answer=2520.

    main:
      n=20,
      answer=232792560.

    extended:
      n=50,
      answer=3099044504245996706400.

      n=100,
      answer=69720375229712477164533808935312303556800.


  Answer: 232792560
  URL: https://projecteuler.net/problem=5
"""
from __future__ import annotations

from functools import reduce
from math import gcd

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=5, test_case_category=TestCaseCategory.EXTENDED)
def smallest_multiple(*, n: int) -> int:
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=5, time_out_in_seconds=300, mode='evaluate'))
