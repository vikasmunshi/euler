#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 51: Prime Digit Replacements.

  Problem Statement:
    By replacing the 1st digit of the 2-digit number *3, it turns out that six of
    the nine possible values: 13, 23, 43, 53, 73, and 83, are all prime.

    By replacing the 3rd and 4th digits of 56**3 with the same digit, this 5-digit
    number is the first example having seven primes among the ten generated numbers,
    yielding the family: 56003, 56113, 56333, 56443, 56663, 56773, and 56993.
    Consequently 56003, being the first member of this family, is the smallest prime
    with this property.

    Find the smallest prime which, by replacing part of the number (not necessarily
    adjacent digits) with the same digit, is part of an eight prime value family.

  Solution Approach:
    To solve this problem, begin by generating prime numbers and examining their
    digit patterns. Consider various combinations of digit positions that can be
    replaced simultaneously with the same digit, and generate all candidates by
    substituting digits from 0 to 9. For each such pattern, count how many of the
    generated numbers are prime. Use efficient primality testing methods to
    handle large numbers and prune search space by focusing on positions that yield
    significant prime families. The goal is to identify the smallest prime with a
    family of eight primes formed by such replacements.

  Test Cases:
    preliminary:
      num_digits=6,
      prime_run=6,
      answer=13.

      num_digits=6,
      prime_run=7,
      answer=56003.

    main:
      num_digits=6,
      prime_run=8,
      answer=121313.


  Answer: 121313
  URL: https://projecteuler.net/problem=51
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.primes import get_pre_computed_primes_sundaram_sieve, is_prime
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=51, test_case_category=TestCaseCategory.EXTENDED)
def prime_digit_replacements(*, num_digits: int, prime_run: int) -> int:
    for prime in get_pre_computed_primes_sundaram_sieve(max_limit=10 ** num_digits):
        for replaced in '0123456789'[:10 - prime_run]:
            sequence = tuple((new_prime for replacement in '0123456789' if replacement >= replaced if
                              (new_prime := int(str(prime).replace(replaced, replacement))) >= prime and is_prime(
                                      new_prime)))
            if len(sequence) == prime_run:
                return prime
    else:
        raise ValueError('No solution found')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=51, time_out_in_seconds=300, mode='evaluate'))
