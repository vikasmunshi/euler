#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
  Project Euler Problem 9: Special Pythagorean Triplet.

  Problem Statement:
    A Pythagorean triplet is a set of three natural numbers, a < b < c, for which,
    a^2 + b^2 = c^2.

    For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.

    There exists exactly one Pythagorean triplet for which a + b + c = 1000.
    Find the product abc.

  Solution Approach:
    To solve this problem, consider the relationship between the numbers a, b, and
    c that satisfy the Pythagorean theorem and the sum constraint a + b + c = 1000.
    Use algebraic manipulations to express one variable in terms of the others.
    Iterate through possible values of a and b, compute c, and check whether they
    meet both the Pythagorean condition and the sum condition. Be efficient by
    limiting the search space using inequalities and properties of Pythagorean
    triplets. This problem involves a combination of mathematical reasoning about
    integer solutions and a computational search for the unique triplet.

  Test Cases:
    preliminary:
      sum_sides=12,
      answer=60.

    main:
      sum_sides=1000,
      answer=31875000.


  Answer: 31875000
  URL: https://projecteuler.net/problem=9
"""
from __future__ import annotations

from euler.logger import logger
from euler.setup import TestCaseCategory, evaluate, register_solution


@register_solution(euler_problem=9, test_case_category=TestCaseCategory.EXTENDED)
def special_pythagorean_triplet(*, sum_sides: int) -> int:
    try:
        return next((a * b * c for a in range(1, sum_sides // 4 + 1) for b in range(a, sum_sides // 2) for c in
                     (sum_sides - a - b,) if a ** 2 + b ** 2 == c ** 2))
    except StopIteration:
        raise ValueError(f'No Pythagorean triplet exists with sum {sum_sides}')


if __name__ == '__main__':
    logger.setLevel('ERROR')
    raise SystemExit(evaluate(euler_problem=9, time_out_in_seconds=300, mode='evaluate'))
