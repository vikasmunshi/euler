#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 41: Pandigital Prime.

  Problem Statement:
    We shall say that an n-digit number is pandigital if it makes use of all the digits
    1 to n exactly once. For example, 2143 is a 4-digit pandigital and is also prime.

    What is the largest n-digit pandigital prime that exists?

  Solution Approach:
    To solve this problem, you can use a combinatorial approach combined with
    prime checking. Generate permutations of digits from 1 to n for different values
    of n, starting from the largest possible n-digit pandigital numbers and moving
    downwards. For each permutation, convert it into a number and test if it is prime.
    Since the problem asks for the largest pandigital prime, you can stop once you
    find the first prime during this descending search. Efficient primality testing
    will significantly improve performance. Additionally, consider properties of
    digit sums to eliminate certain pandigital lengths without exhaustive search.

  Test Cases:
    main:
      answer=7652413.


  Answer: 7652413
  URL: https://projecteuler.net/problem=41
"""
from __future__ import annotations

from euler.logger import logger
from euler.maths.pandigital_numbers import gen_n_digit_pandigital_numbers
from euler.maths.primes import is_prime
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=41, test_case_category=TestCaseCategory.EXTENDED)
def pandigital_prime() -> int:
    pandigital_primes = (number
                         for length in (7, 4)
                         for number in (gen_n_digit_pandigital_numbers(length, descending=True))
                         if is_prime(number))
    return next(pandigital_primes)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=41, time_out_in_seconds=300, mode='evaluate'))
