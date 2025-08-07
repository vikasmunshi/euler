#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 70: Totient Permutation.

  Problem Statement:
    Euler's totient function, \u03d5(n) [sometimes called the phi function], is
    used to determine the number of positive numbers less than or equal to n which
    are relatively prime to n. For example, as 1, 2, 4, 5, 7, and 8, are all less
    than nine and relatively prime to nine, \u03d9(9) = 6.

    The number 1 is considered to be relatively prime to every positive number, so
    \u03d9(1) = 1.

    Interestingly, \u03d9(87109) = 79180, and it can be seen that 87109 is a
    permutation of 79180.

    Find the value of n, 1 < n < 10**7, for which \u03d9(n) is a permutation of n
    and the ratio n / \u03d9(n) produces a minimum.

  Solution Approach:
    To solve this problem, start by understanding Euler's totient function and
    its properties. One key insight is that the totient function is multiplicative
    over prime factors. To find n for which \u03d9(n) is a permutation of n, you
    can:

    1. Generate candidates for n below 10 million, focusing on integers with
       relatively simple prime factorizations.
    2. Calculate \u03d9(n) using prime factorization: \u03d9(n) = n * \u2211(1 - 1/p),
       where the product is over the distinct prime factors p of n.
    3. Check if \u03d9(n) is a digit permutation of n by comparing sorted digits.
    4. Track the minimum ratio n/\u03d9(n) for valid n found.

    Efficiently generating and testing candidate numbers using sieves and prime
    lists, as well as pruning based on bounds of the ratio, will aid performance.
    This approach combines number theory, prime factorization, and permutation
    checks.

  Test Cases:
    main:
      n=10000000,
      answer=8319823.

    extended:
      n=100000000,
      answer=99836521.


  Answer: 8319823
  URL: https://projecteuler.net/problem=70
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.primes import gen_primes_sieve_eratosthenes
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=70, test_case_category=TestCaseCategory.EXTENDED)
def totient_permutation(*, n: int) -> int:
    min_ratio: float = float('inf')
    min_n: int = 0
    sqrt_n = int(n ** 0.5)
    min_prime_1, max_prime_1 = (sqrt_n // 2, sqrt_n)
    for prime_1 in (p for p in gen_primes_sieve_eratosthenes() if p > min_prime_1):
        if prime_1 > max_prime_1:
            break
        min_prime_2, max_prime_2 = (prime_1 + 2, int(n / prime_1))
        for prime_2 in (p for p in gen_primes_sieve_eratosthenes() if p > min_prime_2):
            if prime_2 > max_prime_2:
                break
            if sorted(str((number := (prime_1 * prime_2)))) == sorted(
                    str((totient := ((prime_1 - 1) * (prime_2 - 1))))):
                if (ratio := (number / totient)) < min_ratio:
                    min_ratio, min_n = (ratio, number)
    return min_n


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=70, time_out_in_seconds=300, mode='evaluate'))
