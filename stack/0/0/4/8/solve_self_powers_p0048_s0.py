#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0048/p0048.py :: solve_self_powers_p0048_s0.

Project Euler Problem 48: Self Powers.

Problem Statement:
    The series, 1^1 + 2^2 + 3^3 + ... + 10^10 = 10405071317.

    Find the last ten digits of the series, 1^1 + 2^2 + 3^3 + ... + 1000^1000.

Solution Approach:
    Use modular arithmetic with modulus 10^10 to efficiently compute
    the sum of i^i for i in 1 to 1000. Avoid computing full powers directly
    by taking mod at each step. Time complexity O(n), n=1000 here, which is efficient.

Answer: 9110846700
URL: https://projecteuler.net/problem=48"""
from __future__ import annotations


def solve(*, limit: int) -> int:
    modulo: int = 10 ** 10
    result: int = 0
    for i in range(1, limit + 1):
        term = pow(i, i, modulo)
        result = (result + term) % modulo
    return result


if __name__ == '__main__':
    import sys

    print(solve(limit=int(sys.argv[1])))
