#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0057/p0057.py :: solve_square_root_convergents_p0057_s0.

Project Euler Problem 57: Square Root Convergents.

Problem Statement:
    It is possible to show that the square root of two can be expressed as an
    infinite continued fraction.

        sqrt 2 = 1 + 1 / (2 + 1 / (2 + 1 / (2 + ...)))

    By expanding this for the first four iterations, we get:

        1 + 1/2 = 3/2 = 1.5
        1 + 1/(2 + 1/2) = 7/5 = 1.4
        1 + 1/(2 + 1/(2 + 1/2)) = 17/12 = 1.41666 ...
        1 + 1/(2 + 1/(2 + 1/(2 + 1/2))) = 41/29 = 1.41379 ...

    The next three expansions are 99/70, 239/169, and 577/408, but the eighth
    expansion, 1393/985, is the first example where the number of digits in the
    numerator exceeds the number of digits in the denominator.

    In the first one-thousand expansions, how many fractions contain a numerator
    with more digits than the denominator?

Solution Approach:
    Use iterative calculation of the numerator and denominator of each expansion.
    Track the lengths of numerator and denominator digits for each term.
    Count how many times numerator digits exceed denominator digits.
    This uses number theory and iterative fraction update formulas.
    Time complexity is O(n) for n expansions, which is efficient for 1000 terms.

Answer: 153
URL: https://projecteuler.net/problem=57"""
from __future__ import annotations

import sys
from sys import set_int_max_str_digits


def solve(*, expansions: int) -> int:
    numerator, denominator, result = (1, 1, 0)
    for _ in range(expansions):
        numerator, denominator = (numerator + 2 * denominator, numerator + denominator)
        try:
            result += len(str(numerator)) > len(str(denominator))
        except ValueError:
            set_int_max_str_digits(0)
            print(f'sys.set_int_max_str_digits(0) expansions={expansions!r}, '
                  f'len(str(numerator))={len(str(numerator))!r}, len(str(denominator))={len(str(denominator))!r}',
                  file=sys.stderr)
            result += len(str(numerator)) > len(str(denominator))
    return result


if __name__ == '__main__':
    print(solve(expansions=int(sys.argv[1])))
