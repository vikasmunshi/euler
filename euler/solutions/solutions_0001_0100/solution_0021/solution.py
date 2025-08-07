#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 21: Amicable Numbers.

  Problem Statement:
    Let d(n) be defined as the sum of proper divisors of n (numbers less than n which
    divide evenly into n).

    If d(a) = b and d(b) = a, where a is not equal to b, then a and b are an amicable
    pair and each of a and b are called amicable numbers.

    For example, the proper divisors of 220 are 1, 2, 4, 5, 10, 11, 20, 22, 44, 55
    and 110; therefore d(220) = 284. The proper divisors of 284 are 1, 2, 4, 71 and 142;
    so d(284) = 220.

    Evaluate the sum of all the amicable numbers under 10000.

  Solution Approach:
    To solve the problem of finding amicable numbers under 10,000, first create a
    function that computes the sum of proper divisors for any given number n.
    Proper divisors are numbers less than n that divide n evenly.

    Next, iterate through numbers from 1 up to 10,000, compute their sum of proper
    divisors, and check if the resulting paired sums form an amicable pair.
    Specifically, for a given number a, find b = d(a), then verify if d(b) = a and
    a != b.

    To improve efficiency, use a sieve or caching to avoid repeated divisor sum
    calculations. Accumulate all numbers that belong to amicable pairs, and finally
    compute their total sum. This approach combines number theory knowledge with
    algorithmic optimization techniques.

  Test Cases:
    main:
      max_num=10000,
      answer=31626.


  Answer: 31626
  URL: https://projecteuler.net/problem=21
"""
from __future__ import annotations

from functools import lru_cache

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@lru_cache()
def sum_factors(n: int) -> int:
    n_sqrt = int(n ** 0.5)
    return 1 + sum((i + n // i for i in range(2, n_sqrt + 1) if n % i == 0)) - (n_sqrt if n_sqrt ** 2 == n else 0)


@register_solution(euler_problem=21, test_case_category=TestCaseCategory.EXTENDED)
def amicable_numbers(*, max_num: int) -> int:
    return sum((x for x in range(2, max_num + 1) if (y := sum_factors(x)) != x and sum_factors(y) == x))


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=21, time_out_in_seconds=300, mode='evaluate'))
