#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 87: Prime Power Triples.

  Problem Statement:
    The smallest number expressible as the sum of a prime square, prime cube, and
    prime fourth power is 28. In fact, there are exactly four numbers below
    fifty that can be expressed in such a way:

        28 = 2 x 2 + 2 x 2 x 2 + 2 x 2 x 2 x 2
        33 = 3 x 3 + 2 x 2 x 2 + 2 x 2 x 2 x 2
        49 = 5 x 5 + 2 x 2 x 2 + 2 x 2 x 2 x 2
        47 = 2 x 2 + 3 x 3 x 3 + 2 x 2 x 2 x 2

    How many numbers below fifty million can be expressed as the sum of a prime
    square, prime cube, and prime fourth power?

  Solution Approach:
    To solve this problem, generate lists of prime numbers up to the limits
    imposed by the given range (fifty million) for squares, cubes, and fourth
    powers. Then compute all possible sums of a prime square, prime cube, and
    prime fourth power. Use an efficient data structure, such as a set, to
    store unique sums and avoid duplicates. Finally, count how many unique
    sums are below fifty million. Efficient prime generation algorithms,
    like the Sieve of Eratosthenes, can be used to produce the prime lists.
    This approach leverages number theory properties and efficient search
    techniques to enumerate valid sums within constraints.

  Test Cases:
    preliminary:
      max_num=50,
      answer=4.

    main:
      max_num=50000000,
      answer=1097343.


  Answer: 1097343
  URL: https://projecteuler.net/problem=87
"""
from __future__ import annotations

from math import sqrt
from typing import Generator, Tuple

from euler.logger import logger
from euler.maths.primes import get_pre_computed_primes_sundaram_sieve
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=87, test_case_category=TestCaseCategory.EXTENDED)
def prime_power_triples(*, max_num: int) -> int:
    primes: Tuple[int, ...] = get_pre_computed_primes_sundaram_sieve(max_limit=int(sqrt(max_num)))
    numbers = set()
    max_quadruple_cube: int = max_num - 4
    max_quadruple: int = max_quadruple_cube - 8
    for quadruple in prime_powers(primes, 4):
        if quadruple > max_quadruple:
            break
        for cube in prime_powers(primes, 3):
            if (quadruple_cube := (quadruple + cube)) > max_quadruple_cube:
                break
            for square in prime_powers(primes, 2):
                if (number := (quadruple_cube + square)) >= max_num:
                    break
                numbers.add(number)
    return len(numbers)


def prime_powers(primes: Tuple[int, ...], exponent: int) -> Generator[int, None, None]:
    for base in primes:
        yield (base ** exponent)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=87, time_out_in_seconds=300, mode='evaluate'))
