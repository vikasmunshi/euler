#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 77: Prime Summations.

  Problem Statement:
    It is possible to write ten as the sum of primes in exactly five different
    ways:
    7 + 3
    5 + 5
    5 + 3 + 2
    3 + 3 + 2 + 2
    2 + 2 + 2 + 2 + 2

    What is the first value which can be written as the sum of primes in over
    five thousand different ways?

  Solution Approach:
    To solve this problem, one should consider the concept of partitioning
    numbers into sums of prime numbers. A dynamic programming approach can
    efficiently count the ways to express integers as sums of primes by building
    up from smaller values. Begin by generating a list of prime numbers up to a
    certain limit using the Sieve of Eratosthenes. Then use a table to store the
    number of ways to write each integer as a sum of primes, updating this table
    iteratively for each prime. Continue until the count for the number of ways
    exceeds five thousand, identifying the first such number.

  Test Cases:
    preliminary:
      num_prime_partitions=5,
      answer=10.

      num_prime_partitions=50,
      answer=25.

      num_prime_partitions=500,
      answer=45.

    main:
      num_prime_partitions=5000,
      answer=71.

    extended:
      num_prime_partitions=50000,
      answer=104.


  Answer: 71
  URL: https://projecteuler.net/problem=77
"""
from __future__ import annotations

from itertools import count

from euler.logger import logger
from euler.maths.integer_partitions import get_prime_partitions, num_prime_integer_partitions
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=77, test_case_category=TestCaseCategory.PRELIMINARY)
def prime_summations_list_prime_partitions(*, num_prime_partitions: int) -> int:
    for n in count(2):
        if len(get_prime_partitions(number=n, slots=n)) >= num_prime_partitions:
            return n
    return -1


@register_solution(euler_problem=77, test_case_category=TestCaseCategory.EXTENDED)
def prime_summations_dynamic_recursion(*, num_prime_partitions: int) -> int:
    for n in count(1):
        if num_prime_integer_partitions(number=n, slots=n) >= num_prime_partitions:
            return n
    return -1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=77, time_out_in_seconds=300, mode='evaluate'))
