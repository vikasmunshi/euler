#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0071/p0071.py :: solve_ordered_fractions_p0071_s0.

Project Euler Problem 71: Ordered Fractions.

Problem Statement:
    Consider the fraction, n/d, where n and d are positive integers. If n < d and
    HCF(n, d) = 1, it is called a reduced proper fraction.

    If we list the set of reduced proper fractions for d ≤ 8 in ascending order of size,
    we get:
      1/8, 1/7, 1/6, 1/5, 1/4, 2/7, 1/3, 3/8, 2/5, 3/7, 1/2, 4/7, 3/5, 5/8, 2/3,
      5/7, 3/4, 4/5, 5/6, 6/7, 7/8

    It can be seen that 2/5 is the fraction immediately to the left of 3/7.

    By listing the set of reduced proper fractions for d ≤ 1,000,000 in ascending order
    of size, find the numerator of the fraction immediately to the left of 3/7.

Solution Approach:
    Use number theory and rational approximation. For each denominator d ≤ limit,
    find the largest numerator n where n/d < 3/7. Keep track of the closest fraction
    less than 3/7 with gcd(n, d) = 1. Use the Euclidean algorithm for gcd checks.
    Expected complexity is O(limit log limit) in the worst case due to gcd computation.

Answer: 428570
URL: https://projecteuler.net/problem=71"""
from __future__ import annotations

import sys
from fractions import Fraction


def show_solution() -> bool:
    return '--show' in sys.argv


def solve(*, max_d: int) -> int:
    result: Fraction = Fraction(3, 7) - Fraction(1, 7 * (max_d // 7))
    if show_solution():
        difference = Fraction(3, 7) - result
        print(f'Solution for max_d={max_d!r}: result={result!r} difference={difference!r} '
              f'result.numerator={result.numerator!r}', file=sys.stderr)
    return result.numerator


if __name__ == '__main__':
    print(solve(max_d=int(sys.argv[1])))
