#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0073/p0073.py :: solve_counting_fractions_in_a_range_p0073_s2.

Project Euler Problem 73: Counting Fractions in a Range.

Problem Statement:
    Consider the fraction, n/d, where n and d are positive integers. If n < d and
    HCF(n, d) = 1, it is called a reduced proper fraction.

    If we list the set of reduced proper fractions for d ≤ 8 in ascending order of
    size, we get:
    1/8, 1/7, 1/6, 1/5, 1/4, 2/7, 1/3, 3/8, 2/5, 3/7, 1/2, 4/7, 3/5, 5/8, 2/3,
    5/7, 3/4, 4/5, 5/6, 6/7, 7/8

    It can be seen that there are 3 fractions between 1/3 and 1/2.

    How many fractions lie between 1/3 and 1/2 in the sorted set of reduced proper
    fractions for d ≤ 12000?

Solution Approach:
    Use number theory and Farey sequences or Euler's totient function techniques.
    Efficient counting can be done by recursively counting fractions in the range
    using mediant property or by leveraging the Farey sequence properties.
    Complexity is primarily determined by efficient gcd calculations and careful
    interval counting within given denominator constraints.

Answer: 7295372
URL: https://projecteuler.net/problem=73"""
from __future__ import annotations

from typing import List


def solve(*, max_d: int) -> int:
    def rank(n: int, d: int) -> int:
        len_data: int = max_d + 1
        data: List[int] = [i * n // d for i in range(len_data)]
        for i in range(1, len_data):
            for j in range(2 * i, len_data, i):
                data[j] -= data[i]
        return sum(data)

    return rank(n=1, d=2) - rank(n=1, d=3) - 1


if __name__ == '__main__':
    import sys

    print(solve(max_d=int(sys.argv[1])))
