#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0006/p0006.py :: solve_sum_square_difference_p0006_s0.

Project Euler Problem 6: Sum Square Difference.

Problem Statement:
    The sum of the squares of the first ten natural numbers is,
    1^2 + 2^2 + ... + 10^2 = 385.
    The square of the sum of the first ten natural numbers is,
    (1 + 2 + ... + 10)^2 = 55^2 = 3025.
    Hence the difference between the sum of the squares of the first ten natural
    numbers and the square of the sum is 3025 - 385 = 2640.

    Find the difference between the sum of the squares of the first one hundred
    natural numbers and the square of the sum.

Solution Approach:
    Use mathematical formulas for sums of integers and sums of squares:
        Sum of first n natural numbers: n(n+1)/2
        Sum of squares of first n natural numbers: n(n+1)(2n+1)/6
    Compute square of sum and sum of squares separately, then take the difference.
    Time complexity is O(1) as this uses direct formulas.

Answer: 25164150
URL: https://projecteuler.net/problem=6"""
from __future__ import annotations


def solve(*, n: int) -> int:
    return (n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6


if __name__ == '__main__':
    import sys

    print(solve(n=int(sys.argv[1])))
