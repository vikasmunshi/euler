#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 100: Arranged Probability.

  Problem Statement:
    If a box contains twenty-one coloured discs, composed of fifteen blue discs and
    six red discs, and two discs were taken at random, it can be seen that the
    probability of taking two blue discs, P(BB) = (15/21) x (14/20) = 1/2.

    The next such arrangement, for which there is exactly 50% chance of taking
    two blue discs at random, is a box containing eighty-five blue discs and
    thirty-five red discs.

    By finding the first arrangement to contain over 10^12 = 1 000 000 000 000
    discs in total, determine the number of blue discs that the box would contain.

  Solution Approach:
    This problem involves finding specific integer solutions to a probability
    condition involving combinations of discs. The probability of drawing two
    blue discs is given by a fraction involving the counts of blue and total
    discs. By setting this probability equal to 1/2 and using variables for blue
    and total discs, the problem reduces to finding integral solutions of a
    quadratic Diophantine equation. A fruitful approach involves identifying that
    the problem can be represented using Pell's equation, which is a well-known
    form in number theory. One can use the properties of Pell's equation to
    generate successive integer solutions starting from the known initial cases.
    Efficiently iterating through these solutions to find the first exceeding
    the total discs limit (10^12) will yield the number of blue discs. Implementing
    this approach requires careful handling of large integers and understanding
    of recurrence relations or continued fraction expansions related to Pell's
    equation.

  Test Cases:
    preliminary:
      total_discs=21,
      answer=15.

      total_discs=120,
      answer=85.

    main:
      total_discs=1000000000000,
      answer=756872327473.


  Answer: 756872327473
  URL: https://projecteuler.net/problem=100
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=100, test_case_category=TestCaseCategory.EXTENDED)
def arranged_probability(*, total_discs: int) -> int:
    x, y = (1, 1)
    while True:
        x, y = (3 * x + 4 * y, 2 * x + 3 * y)
        n = (x + 1) // 2
        b = (y + 1) // 2
        if n >= total_discs:
            return b


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=100, time_out_in_seconds=300, mode='evaluate'))
