#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 69: Totient Maximum.

  Problem Statement:
    Euler's totient function, \u03d5(n) [sometimes called the phi function], is
    defined as the number of positive integers not exceeding n which are
    relatively prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all
    less than or equal to nine and relatively prime to nine, \u03d5(9) = 6.

    n   Relatively Prime  \u03d5(n)    n / \u03d5(n)
    2   1                1        2
    3   1,2              2        1.5
    4   1,3              2        2
    5   1,2,3,4          4        1.25
    6   1,5              2        3
    7   1,2,3,4,5,6      6        1.1666...
    8   1,3,5,7          4        2
    9   1,2,4,5,7,8      6        1.5
    10  1,3,7,9          4        2.5

    It can be seen that n = 6 produces a maximum n / \u03d5(n) for n \u2264 10.

    Find the value of n \u2264 1 000 000 for which n / \u03d5(n) is a maximum.

  Solution Approach:
    To solve this problem, understand that \u03d5(n) counts integers relatively
    prime to n. The ratio n / \u03d5(n) is maximized when n has many small prime
    factors. To find the maximum n / \u03d5(n) for n up to one million, use the
    fact that \u03d5 is multiplicative and for a prime p, \u03d5(p) = p - 1. The
    ratio n / \u03d5(n) can be expressed as a product over the primes dividing n
    of p / (p - 1). Therefore, the problem reduces to multiplying small primes
    in ascending order until the product exceeds one million. The largest
    product under one million maximizing n / \u03d5(n) is the answer. Efficient
    computation requires prime generation, careful product accumulation, and
    checking values.

  Test Cases:
    preliminary:
      n=10,
      answer=6.

      n=100,
      answer=30.

      n=1000,
      answer=210.

      n=10000,
      answer=2310.

      n=100000,
      answer=30030.

    main:
      n=1000000,
      answer=510510.

    extended:
      n=10000000,
      answer=9699690.

      n=100000000,
      answer=9699690.

      n=1000000000,
      answer=223092870.

      n=10000000000,
      answer=6469693230.

      n=100000000000,
      answer=6469693230.

      n=1000000000000,
      answer=200560490130.


  Answer: 510510
  URL: https://projecteuler.net/problem=69
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.primes import gen_primes_sieve_eratosthenes
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=69, test_case_category=TestCaseCategory.EXTENDED)
def totient_maximum(*, n: int) -> int:
    result: int = 1
    for prime_num in gen_primes_sieve_eratosthenes():
        if (result := (result * prime_num)) > n:
            result = result // prime_num
            break
    return result


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=69, time_out_in_seconds=300, mode='evaluate'))
