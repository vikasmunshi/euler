#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 65: Convergents Of E.

  Problem Statement:
    The square root of 2 can be written as an infinite continued fraction.

    sqrt(2) = 1 + 1 / (2 + 1 / (2 + 1 / (2 + 1 / (2 + ...))))

    The infinite continued fraction can be written, sqrt(2) = [1; (2)], (2) indicates
    that 2 repeats ad infinitum. In a similar way, sqrt(23) = [4; (1, 3, 1, 8)].

    It turns out that the sequence of partial values of continued fractions for square
    roots provide the best rational approximations. Let us consider the convergents
    for sqrt(2).

    1 + 1 / 2 = 3 / 2
    1 + 1 / (2 + 1 / 2) = 7 / 5
    1 + 1 / (2 + 1 / (2 + 1 / 2)) = 17 / 12
    1 + 1 / (2 + 1 / (2 + 1 / (2 + 1 / 2))) = 41 / 29

    Hence the sequence of the first ten convergents for sqrt(2) are:

    1, 3 / 2, 7 / 5, 17 / 12, 41 / 29, 99 / 70, 239 / 169, 577 / 408, 1393 / 985,
    3363 / 2378, ...

    What is most surprising is that the important mathematical constant,
    e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, ... , 1, 2k, 1, ...].

    The first ten terms in the sequence of convergents for e are:

    2, 3, 8 / 3, 11 / 4, 19 / 7, 87 / 32, 106 / 39, 193 / 71, 1264 / 465,
    1457 / 536, ...

    The sum of digits in the numerator of the 10th convergent is 1 + 4 + 5 + 7 = 17.

    Find the sum of digits in the numerator of the 100th convergent of the continued
    fraction for e.

  Solution Approach:
    To solve this problem, first understand the pattern of the continued fraction
    for the mathematical constant e. The sequence of coefficients in the continued
    fraction follows a distinct pattern involving 1, 2k, and 1 where k increases.

    Implement a method to generate these coefficients for the first 100 terms. Then,
    use the recurrence relations for convergents of continued fractions to compute the
    numerator and denominator of each convergent recursively.

    Once the numerator of the 100th convergent is obtained, calculate the sum of its
    digits. Efficient handling of large integers is necessary for accurate computation.

    This approach requires knowledge of continued fractions, their convergents, and
    basic number manipulations for digit summation.

  Test Cases:
    preliminary:
      convergent_num=10,
      answer=17.

    main:
      convergent_num=100,
      answer=272.

    extended:
      convergent_num=1000,
      answer=4034.

      convergent_num=10000,
      answer=55322.


  Answer: 272
  URL: https://projecteuler.net/problem=65
"""
from __future__ import annotations

from fractions import Fraction

from euler.logger import logger
from euler.maths.sum_digits import sum_digits
from euler.setup import TestCaseCategory, evaluate, register_solution
from euler.sys_utils import set_resource_limits


def e_denominator(n: int) -> int:
    if n == 1:
        return 2
    elif n % 3 == 0:
        return 2 * n // 3
    else:
        return 1


def nth_convergent_of_e(n: int, *, _n: int = 1) -> Fraction | int:
    if n == _n:
        return e_denominator(_n)
    return e_denominator(_n) + Fraction(1, nth_convergent_of_e(n, _n=_n + 1))


@register_solution(euler_problem=65, test_case_category=TestCaseCategory.EXTENDED)
@set_resource_limits(recursion_var='convergent_num', multiplier=1, set_int_max_str=True, when='always')
def convergents_of_e(*, convergent_num: int) -> int:
    return sum_digits(nth_convergent_of_e(convergent_num).numerator)


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=65, time_out_in_seconds=300, mode='evaluate'))
