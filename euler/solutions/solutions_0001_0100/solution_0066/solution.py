#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 66: Diophantine Equation.

  Problem Statement:
    Consider quadratic Diophantine equations of the form:
    x^2 - Dy^2 = 1

    For example, when D = 13, the minimal solution in x is
    649^2 - 13 x 180^2 = 1.

    It can be assumed that there are no solutions in positive integers when
    D is square.

    By finding minimal solutions in x for D = {2, 3, 5, 6, 7}, we obtain the
    following:

    3^2 - 2 x 2^2 = 1
    2^2 - 3 x 1^2 = 1
    9^2 - 5 x 4^2 = 1
    5^2 - 6 x 2^2 = 1
    8^2 - 7 x 3^2 = 1

    Hence, by considering minimal solutions in x for D less than or equal to 7,
    the largest x is obtained when D = 5.

    Find the value of D less than or equal to 1000 in minimal solutions of x
    for which the largest value of x is obtained.

  Solution Approach:
    This problem involves solving Pell's equation, a classical quadratic
    Diophantine equation of the form x^2 - D y^2 = 1, for various non-square
    integers D. The goal is to find the minimal solutions for x, where the
    solution (x, y) are positive integers, and identify which D gives the
    largest minimal x for D up to 1000.

    To solve this computationally, one can use the method of continued
    fractions to find the fundamental solution (minimal positive x) for each
    D. The continued fraction expansion of the square root of D is periodic,
    and from this the minimal solution to Pell's equation can be derived.

    By iterating over all D values from 1 to 1000 (excluding squares), and
    computing their fundamental solutions, the D with the largest x can be
    efficiently identified. Implementations typically benefit from efficient
    generation and truncation of continued fractions, and careful handling
    of large integer arithmetic because solutions can grow very large.

  Test Cases:
    preliminary:
      max_d=7,
      answer=5.

    main:
      max_d=1000,
      answer=661.

    extended:
      max_d=10000,
      answer=9949.


  Answer: 661
  URL: https://projecteuler.net/problem=66
"""
from __future__ import annotations

from fractions import Fraction
from math import floor, sqrt
from operator import itemgetter
from typing import Tuple

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


def compute_nth_convergent(continued_fraction: Tuple[int, ...], n: int) -> Fraction:
    period_length: int = len(continued_fraction) - 1
    convergent: Fraction = Fraction(continued_fraction[(n - 1) % period_length + 1], 1)
    for i in range(n - 1, 0, -1):
        term_index = (i - 1) % period_length + 1
        term = Fraction(continued_fraction[term_index], 1)
        convergent = term + Fraction(1, convergent)
    convergent = Fraction(continued_fraction[0], 1) + Fraction(1, convergent)
    return convergent


def find_fundamental_solution_to_pell_equation(d: int) -> Tuple[int, int]:
    if (sqrt_d := sqrt(d)).is_integer():
        return (1, 0)
    continued_fraction: Tuple[int, ...] = (floor(sqrt_d),)
    m: int = 0
    n: int = 1
    while continued_fraction[-1] != 2 * continued_fraction[0]:
        m = n * continued_fraction[-1] - m
        n = (d - m * m) // n
        continued_fraction += (floor((sqrt_d + m) / n),)
    if (len_continued_fraction := len(continued_fraction)) % 2 == 0:
        return compute_nth_convergent(continued_fraction, 2 * len_continued_fraction - 3).as_integer_ratio()
    else:
        return compute_nth_convergent(continued_fraction, len_continued_fraction - 2).as_integer_ratio()


@register_solution(euler_problem=66, test_case_category=TestCaseCategory.EXTENDED)
def diophantine_equation(*, max_d: int) -> int:
    return max(((find_fundamental_solution_to_pell_equation(d)[0], d) for d in range(2, max_d + 1) if
                sqrt(d).is_integer() is False), key=itemgetter(0))[-1]


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=66, time_out_in_seconds=300, mode='evaluate'))
