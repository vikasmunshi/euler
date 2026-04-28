#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0053/p0053.py :: solve_combinatoric_selections_p0053_s0.

Project Euler Problem 53: Combinatoric Selections.

Problem Statement:
    There are exactly ten ways of selecting three from five, 12345:
    123, 124, 125, 134, 135, 145, 234, 235, 245, and 345.
    In combinatorics, we use the notation, C(5, 3) = 10.

    In general, C(n, r) = n! / (r! (n-r)!), where r <= n, n! = n * (n-1) * ... * 3 * 2 * 1,
    and 0! = 1.

    It is not until n = 23, that a value exceeds one-million:
    C(23, 10) = 1144066.

    How many, not necessarily distinct, values of C(n, r) for 1 <= n <= 100, are greater than
    one-million?

Solution Approach:
    Use combinatorics to compute binomial coefficients efficiently.
    Iterate over n from 1 to 100, and r from 0 to n.
    Use either direct formula with factorial or iterative combinatorial calculation
    to avoid large intermediate values.
    Count how many values exceed 1,000,000.
    Time complexity is roughly O(n^2), which is efficient for n=100.

Answer: 4075
URL: https://projecteuler.net/problem=53"""
from __future__ import annotations


def solve(*, max_n: int, threshold: int) -> int:
    count = 0
    for n in range(1, max_n + 1):
        c = 1
        for r in range(0, n // 2 + 1):
            if c > threshold:
                count += n - 2 * r + 1
                break
            else:
                c = c * (n - r) // (r + 1)
    return count


if __name__ == '__main__':
    import sys

    print(solve(max_n=int(sys.argv[1]), threshold=int(sys.argv[2])))
