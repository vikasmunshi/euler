#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0001/p0001.py :: solve_multiples_of_3_or_5_p0001_s1.

Project Euler Problem 1: Multiples of 3 or 5.

Problem Statement:
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we
    get 3, 5, 6 and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.

Solution Approach:
    Use inclusion–exclusion principle. Sum multiples of 3 and 5, then subtract multiples
    of 15 to avoid double counting. Employ arithmetic progression sums for constant time.

Answer: 233168
URL: https://projecteuler.net/problem=1"""
from __future__ import annotations


def solve(*, max_limit: int) -> int:
    result: int = 0
    for term in range(0, max_limit):
        if term % 3 == 0 or term % 5 == 0:
            result += term
    return result


if __name__ == '__main__':
    import sys

    print(solve(max_limit=int(sys.argv[1])))
