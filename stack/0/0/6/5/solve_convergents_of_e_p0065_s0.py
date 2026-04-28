#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0065/p0065.py :: solve_convergents_of_e_p0065_s0.

Project Euler Problem 65: Convergents of e.

Problem Statement:
    The square root of 2 can be written as an infinite continued fraction.

    sqrt(2) = 1 + 1/(2 + 1/(2 + 1/(2 + 1/(2 + ...))))

    The infinite continued fraction can be written, sqrt(2) = [1; (2)], (2)
    indicates that 2 repeats ad infinitum. In a similar way, sqrt(23) = [4; (1,
    3, 1, 8)].

    It turns out that the sequence of partial values of continued fractions for
    square roots provide the best rational approximations. Let us consider the
    convergents for sqrt(2).

        1 + 1/2 = 3/2
        1 + 1/(2 + 1/2) = 7/5
        1 + 1/(2 + 1/(2 + 1/2)) = 17/12
        1 + 1/(2 + 1/(2 + 1/(2 + 1/2))) = 41/29

    Hence the sequence of the first ten convergents for sqrt(2) are:
    1, 3/2, 7/5, 17/12, 41/29, 99/70, 239/169, 577/408, 1393/985, 3363/2378, ...

    What is most surprising is that the important mathematical constant,
    e = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, ... , 1, 2k, 1, ...]

    The first ten terms in the sequence of convergents for e are:
    2, 3, 8/3, 11/4, 19/7, 87/32, 106/39, 193/71, 1264/465, 1457/536, ...

    The sum of digits in the numerator of the 10th convergent is 1 + 4 + 5 + 7 = 17.

    Find the sum of digits in the numerator of the 100th convergent of the
    continued fraction for e.

Solution Approach:
    Use continued fraction expansions for e based on known patterns for partial
    denominators.
    Compute convergents using numerator/denominator recurrence relations.
    Extract numerator of the 100th convergent and sum its digits.
    As operations involve large integers only, Python built-in arbitrary precision
    integers are used.
    Time complexity roughly O(n) with n=100, space O(1).

Answer: 272
URL: https://projecteuler.net/problem=65"""
from __future__ import annotations

from fractions import Fraction


def sum_digits(n: int) -> int:
    total: int = 0
    while n:
        total += n % 10
        n //= 10
    return total


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


def solve(*, convergent_num: int) -> int:
    return sum_digits(nth_convergent_of_e(convergent_num).numerator)


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(10 ** 6)
    print(solve(convergent_num=int(sys.argv[1])))
