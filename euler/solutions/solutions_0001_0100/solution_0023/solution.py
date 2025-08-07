#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 23: Non Abundant Sums.

  Problem Statement:
    A perfect number is a number for which the sum of its proper divisors is exactly
    equal to the number. For example, the sum of the proper divisors of 28 would be
    1 + 2 + 4 + 7 + 14 = 28, which means that 28 is a perfect number.

    A number n is called deficient if the sum of its proper divisors is less than n
    and it is called abundant if this sum exceeds n.

    As 12 is the smallest abundant number, 1 + 2 + 3 + 4 + 6 = 16, the smallest
    number that can be written as the sum of two abundant numbers is 24. By
    mathematical analysis, it can be shown that all integers greater than 28123 can
    be written as the sum of two abundant numbers. However, this upper limit cannot
    be reduced any further by analysis even though it is known that the greatest
    number that cannot be expressed as the sum of two abundant numbers is less than
    this limit.

    Find the sum of all the positive integers which cannot be written as the sum of
    two abundant numbers.

  Solution Approach:
    To solve this problem, start by understanding the classification of numbers
    based on their proper divisors: perfect, deficient, and abundant. Compute the
    abundant numbers up to the given upper bound (28123) by summing the proper
    divisors of each number. Next, generate all possible sums of two abundant numbers
    within this range. Identify all positive integers that cannot be expressed as the
    sum of two abundant numbers by checking which numbers are not in the generated
    sum set. Finally, sum these identified numbers to get the desired result.
    Using efficient methods to find divisors and leveraging set operations will help
    handle the computations effectively within a reasonable time frame.

  Test Cases:
    main:
      answer=4179871.


  Answer: 4179871
  URL: https://projecteuler.net/problem=23
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=23, test_case_category=TestCaseCategory.EXTENDED)
def non_abundant_sums() -> int:
    abundant_numbers = [i for i in range(12, 28123 - 12) if sum_proper_divisors(i) > i]
    abundant_sums = (a + b for a in abundant_numbers for b in abundant_numbers)
    return sum(set(range(1, 28123 + 1)) - set(abundant_sums))


def sum_proper_divisors(n: int) -> int:
    n_sqrt = int(n ** 0.5)
    return 1 + sum((i + n // i for i in range(2, n_sqrt + 1) if n % i == 0)) - (n_sqrt if n_sqrt ** 2 == n else 0)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=23, time_out_in_seconds=300, mode='evaluate'))
