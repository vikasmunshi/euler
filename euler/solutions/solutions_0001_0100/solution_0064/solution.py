#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 64: Odd Period Square Roots.

  Problem Statement:
    All square roots are periodic when written as continued fractions and can be
    written in the form:

        sqrt(N) = a_0 + 1 / (a_1 + 1 / (a_2 + 1 / (a_3 + ...)))

    For example, let us consider sqrt(23):

        sqrt(23) = 4 + sqrt(23) - 4 = 4 + 1 / (1 / (sqrt(23) - 4)) = 4 + 1 / (1 +
        (sqrt(23) - 3) / 7)

    If we continue we would get the following expansion:

        sqrt(23) = 4 + 1 / (1 + 1 / (3 + 1 / (1 + 1 / (8 + ...))))

    The process can be summarised as follows:

        a_0 = 4, 1 / (sqrt(23) - 4) = (sqrt(23) + 4) / 7 = 1 + (sqrt(23) - 3) / 7
        a_1 = 1, 7 / (sqrt(23) - 3) = 7 (sqrt(23) + 3) / 14 = 3 + (sqrt(23) - 3) / 2
        a_2 = 3, 2 / (sqrt(23) - 3) = 2 (sqrt(23) + 3) / 14 = 1 + (sqrt(23) - 4) / 7
        a_3 = 1, 7 / (sqrt(23) - 4) = 7 (sqrt(23) + 4) / 7 = 8 + sqrt(23) - 4
        a_4 = 8, 1 / (sqrt(23) - 4) = (sqrt(23) + 4) / 7 = 1 + (sqrt(23) - 3) / 7
        a_5 = 1, 7 / (sqrt(23) - 3) = 7 (sqrt(23) + 3) / 14 = 3 + (sqrt(23) - 3) / 2
        a_6 = 3, 2 / (sqrt(23) - 3) = 2 (sqrt(23) + 3) / 14 = 1 + (sqrt(23) - 4) / 7
        a_7 = 1, 7 / (sqrt(23) - 4) = 7 (sqrt(23) + 4) / 7 = 8 + sqrt(23) - 4

    It can be seen that the sequence is repeating. For conciseness, we use the
    notation sqrt(23) = [4; (1,3,1,8)], to indicate that the block (1,3,1,8)
    repeats indefinitely.

    The first ten continued fraction representations of irrational square roots
    are:

        sqrt(2) = [1; (2)], period = 1
        sqrt(3) = [1; (1,2)], period = 2
        sqrt(5) = [2; (4)], period = 1
        sqrt(6) = [2; (2,4)], period = 2
        sqrt(7) = [2; (1,1,1,4)], period = 4
        sqrt(8) = [2; (1,4)], period = 2
        sqrt(10) = [3; (6)], period = 1
        sqrt(11) = [3; (3,6)], period = 2
        sqrt(12) = [3; (2,6)], period = 2
        sqrt(13) = [3; (1,1,1,1,6)], period = 5

    Exactly four continued fractions, for N <= 13, have an odd period.

    How many continued fractions for N <= 10,000 have an odd period?

  Solution Approach:
    To solve this problem, you need to understand the continued fraction expansion
    for square roots of non-square integers. These expansions are periodic, and
    the length of the repeating block (the period) can be computed using the
    process of continued fraction expansion for quadratic irrationals.

    The approach typically involves iterating through all integers N from 2 to
    10,000, skipping perfect squares, and computing the period of the continued
    fraction for sqrt(N). This can be done by tracking the sequence of partial
    denominators and numerators generated during the expansion until the sequence
    repeats.

    Counting how many of these periods are odd will give the desired result.

    Efficient implementation benefits from recognizing the relationship between
    the period and the properties of the quadratic surd, leveraging integer
    arithmetic to avoid precision errors.

  Test Cases:
    preliminary:
      max_limit=13,
      answer=4.

    main:
      max_limit=10000,
      answer=1322.


  Answer: 1322
  URL: https://projecteuler.net/problem=64
"""
from __future__ import annotations

from math import isqrt, sqrt

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=64, test_case_category=TestCaseCategory.EXTENDED)
def odd_period_square_roots(*, max_limit: int) -> int:
    return sum((get_period_length(n) % 2 == 1 for n in range(2, max_limit + 1) if not sqrt(n).is_integer()))


def get_period_length(n: int) -> int:
    a0 = a = isqrt(n)
    d, m, p = (1, 0, [])
    while True:
        m = d * a - m
        d = (n - m ** 2) // d
        a = (a0 + m) // d
        if (m, d, a) in p:
            break
        p.append((m, d, a))
    return len(p)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=64, time_out_in_seconds=300, mode='evaluate'))
