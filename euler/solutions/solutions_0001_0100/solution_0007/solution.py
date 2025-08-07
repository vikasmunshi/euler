#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 7:  10 001St Prime.

  Problem Statement:
    By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see
    that the 6th prime is 13.

    What is the 10,001st prime number?

  Solution Approach:
    To solve this problem, generate prime numbers sequentially and count them
    until reaching the 10,001st prime.

    Efficient prime checking methods such as the Sieve of Eratosthenes or
    optimized trial division should be used to reduce computation time. Implement
    a function to test primality and iterate through natural numbers, counting
    each prime found.

    Since the position is large, avoid simple brute force methods. Consider
    using a dynamic sieve or a segmented sieve approach to handle memory and
    performance effectively.

    The main goal is to identify the exact prime that appears at the 10,001st
    position in the ordered sequence of prime numbers.

  Test Cases:
    preliminary:
      n=6,
      answer=13.

    main:
      n=10001,
      answer=104743.


  Answer: 104743
  URL: https://projecteuler.net/problem=7
"""
from __future__ import annotations

from math import log

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=7, test_case_category=TestCaseCategory.EXTENDED)
def solution_10_001st_prime(*, n: int) -> int:
    if n == 1:
        return 2
    max_expected_value = int(n * log(n))
    numbers = list(range(0, max_expected_value + 1))
    for i in numbers[1:]:
        for j in range(i, max_expected_value + 1):
            try:
                numbers[i + j + 2 * i * j] = 0
            except IndexError:
                break
    return 2 * [i for i in numbers if i != 0][n - 2] + 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=7, time_out_in_seconds=300, mode='evaluate'))
