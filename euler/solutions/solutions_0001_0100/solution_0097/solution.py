#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 97: Large Non Mersenne Prime.

  Problem Statement:
    The first known prime found to exceed one million digits was discovered in
    1999, and is a Mersenne prime of the form 2^6972593 - 1; it contains exactly
    2,098,960 digits. Subsequently other Mersenne primes, of the form 2^p - 1,
    have been found which contain more digits.

    However, in 2004 there was found a massive non-Mersenne prime which contains
    2,357,207 digits: 28433 x 2^7830457 + 1.

    Find the last ten digits of this prime number.

  Solution Approach:
    This problem involves working with very large numbers far beyond standard
    data type limits. To find the last ten digits efficiently, leverage modular
    arithmetic properties, specifically modulo 10^10.

    Because direct computation of 28433 x 2^7830457 + 1 is infeasible, use
    exponentiation by squaring to compute 2^7830457 modulo 10^10.

    Multiply the result by 28433 modulo 10^10 and then add 1, again modulo
    10^10. This approach efficiently reduces the problem to manageable integer
    operations while preserving the last ten digits.

    Implementation can be done in a programming language supporting
    arbitrary-precision integers, but careful use of modular arithmetic
    ensures optimal performance.

  Test Cases:
    main:
      num_digits=10,
      prime=28433 × 2^7830457 + 1,
      answer=8739992577.


  Answer: 8739992577
  URL: https://projecteuler.net/problem=97
"""
from __future__ import annotations

from typing import List

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=97, test_case_category=TestCaseCategory.EXTENDED)
def large_non_mersenne_prime(*, num_digits: int, prime: str) -> int:
    divisor: int = 10 ** num_digits
    prime_parts: List[str] = prime.split()
    number: int
    exponent: int
    number, exponent = (int(prime_parts[0]), int(prime_parts[2][2:]))
    for _ in range(exponent):
        number *= 2
        number %= divisor
    number += 1
    number %= divisor
    return number


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=97, time_out_in_seconds=300, mode='evaluate'))
