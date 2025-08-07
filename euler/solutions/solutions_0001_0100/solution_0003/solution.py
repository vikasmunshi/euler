#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 3: Largest Prime Factor.

  Problem Statement:
    The prime factors of 13195 are 5, 7, 13 and 29.
    What is the largest prime factor of the number 600851475143?

  Solution Approach:
    To solve this problem, start by understanding prime factorization.
    Break down the given number into its prime factors by testing divisibility
    starting from the smallest primes. You can repeatedly divide the number by
    its smallest prime factor until it reduces to 1. The largest prime factor
    encountered during this process is the answer. Efficient algorithms like
    trial division, optimized by checking factors only up to the square root
    of the number, can be used to improve performance. Avoid checking even
    numbers beyond 2 to save computation time.

  Test Cases:
    preliminary:
      number=13195,
      answer=29.

      number=10,
      answer=5.

      number=20,
      answer=5.

    main:
      number=600851475143,
      answer=6857.

    extended:
      number=79376318561249,
      answer=9999991.


  Answer: 6857
  URL: https://projecteuler.net/problem=3
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=3, test_case_category=TestCaseCategory.EXTENDED)
def largest_prime_factor_repeated_division(*, number: int) -> int:
    if number % 2 == 0:
        remaining_number = reduce(number, 2)
        largest_factor = 2
    else:
        remaining_number = number
        largest_factor = 1
    current_factor = 3
    search_limit = int(remaining_number ** 0.5)
    while remaining_number > 1 and current_factor <= search_limit:
        if remaining_number % current_factor == 0:
            remaining_number = reduce(remaining_number, current_factor)
            largest_factor = current_factor
            search_limit = int(remaining_number ** 0.5)
        current_factor += 2
    return remaining_number if remaining_number > 1 else largest_factor


def reduce(num: int, divisor: int) -> int:
    num //= divisor
    while num % divisor == 0:
        num //= divisor
    return num


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=3, time_out_in_seconds=300, mode='evaluate'))
