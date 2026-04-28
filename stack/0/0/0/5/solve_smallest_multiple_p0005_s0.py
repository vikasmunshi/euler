#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0005/p0005.py :: solve_smallest_multiple_p0005_s0.

Project Euler Problem 5: Smallest Multiple.

Problem Statement:
    2520 is the smallest number that can be divided by each of the numbers from 1
    to 10 without any remainder.

    What is the smallest positive number that is evenly divisible by all of the
    numbers from 1 to 20?

Solution Approach:
    Use number theory: find the least common multiple (LCM) of numbers 1 through 20.
    Apply prime factorization or iterative LCM with gcd to combine factors efficiently.
    Time complexity is O(n log n) with efficient gcd.

Answer: 232792560
URL: https://projecteuler.net/problem=5"""
from __future__ import annotations

from functools import reduce
from math import gcd


def solve(*, n: int) -> int:
    return reduce(lambda x, y: x * y // gcd(x, y), range(2, n + 1), 1)


if __name__ == '__main__':
    import sys

    print(solve(n=int(sys.argv[1])))
