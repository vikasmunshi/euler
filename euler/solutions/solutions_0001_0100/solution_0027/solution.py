#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 27: Quadratic Primes.

  Problem Statement:
    Euler discovered the remarkable quadratic formula:

    n^2 + n + 41

    It turns out that the formula will produce 40 primes for the
    consecutive integer values 0 <= n <= 39. However, when n = 40,
    40^2 + 40 + 41 = 40 ( 40 + 1 ) + 41 is divisible by 41, and
    certainly when n = 41, 41^2 + 41 + 41 is clearly divisible by 41.

    The incredible formula n^2 - 79 n + 1601 was discovered, which
    produces 80 primes for the consecutive values 0 <= n <= 79. The
    product of the coefficients, -79 and 1601, is -126479.

    Considering quadratics of the form:

    n^2 + a n + b, where |a| < 1000 and |b| <= 1000

    where |n| is the modulus/absolute value of n
    e.g. |11| = 11 and |-4| = 4

    Find the product of the coefficients, a and b, for the quadratic
    expression that produces the maximum number of primes for
    consecutive values of n, starting with n = 0.

  Solution Approach:
    To solve this problem, programmatically generate quadratic expressions
    of the form n^2 + a n + b with coefficients a and b constrained by
    |a| < 1000 and |b| <= 1000. For each pair (a, b), evaluate the formula
    for consecutive integer values of n starting from 0 and count how many
    primes are produced consecutively. Use an efficient primality test to
    improve performance. Keep track of the coefficients that yield the
    longest sequence of primes. This approach combines trial and error with
    prime testing and requires careful iteration over the coefficient space.

  Test Cases:
    main:
      max_limit=1000,
      answer=-59231.


  Answer: -59231
  URL: https://projecteuler.net/problem=27
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.primes import get_pre_computed_primes_sundaram_sieve, is_prime
from euler.setup import TestCaseCategory, evaluate, register_solution


def prime_run(a: int, b: int) -> int:
    x = 0
    while is_prime(abs(x ** 2 + a * x + b)):
        x += 1
    return x


@register_solution(euler_problem=27, test_case_category=TestCaseCategory.EXTENDED)
def quadratic_primes(*, max_limit: int) -> int:
    return max([max((prime_run(a, b), a * b), (prime_run(a, -b), -a * b), (prime_run(-a, -b), a * b),
                    (prime_run(-a, b), -a * b)) for b in get_pre_computed_primes_sundaram_sieve(max_limit=max_limit) for
                a in
                range(0 if b == 2 else 1, max_limit, 2)])[1]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=27, time_out_in_seconds=300, mode='evaluate'))
