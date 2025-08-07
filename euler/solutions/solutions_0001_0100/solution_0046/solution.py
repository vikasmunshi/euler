#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 46: Goldbachs Other Conjecture.

  Problem Statement:
    It was proposed by Christian Goldbach that every odd composite number can be written
    as the sum of a prime and twice a square.

    9 = 7 + 2 x 1^2
    15 = 7 + 2 x 2^2
    21 = 3 + 2 x 3^2
    25 = 7 + 2 x 3^2
    27 = 19 + 2 x 2^2
    33 = 31 + 2 x 1^2

    It turns out that the conjecture was false.

    What is the smallest odd composite that cannot be written as the sum of a prime and
    twice a square?

  Solution Approach:
    To solve this problem, start by generating a list of prime numbers using an
    efficient algorithm such as the Sieve of Eratosthenes. Then, generate odd
    composite numbers sequentially. For each odd composite, test whether it can be
    expressed as the sum of a prime and twice a square. To verify this, iterate over
    primes less than the composite and check if the difference between the composite
    and the prime is twice a perfect square. Use efficient methods to check for
    perfect squares to optimize the process. The smallest odd composite for which no
    such decomposition holds is the solution. This approach combines prime number
    generation with iterative testing of the given representation.

  Test Cases:
    main:
      answer=5777.


  Answer: 5777
  URL: https://projecteuler.net/problem=46
"""
from __future__ import annotations

from typing import Dict, List, Set

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=46, test_case_category=TestCaseCategory.EXTENDED)
def goldbach_s_other_conjecture() -> int:
    primes: Set[int] = set()
    known_composites: Dict[int, List[int]] = dict()
    current_number = 2
    while True:
        if current_number not in known_composites:
            primes.add(current_number)
            known_composites[current_number ** 2] = [current_number]
        else:
            if current_number % 2 != 0:
                if not any((((current_number - p) / 2) ** 0.5 % 1 == 0 for p in primes if current_number > p != 2)):
                    return current_number
            for p in known_composites[current_number]:
                known_composites.setdefault(p + current_number, []).append(p)
            del known_composites[current_number]
        current_number += 1


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=46, time_out_in_seconds=300, mode='evaluate'))
