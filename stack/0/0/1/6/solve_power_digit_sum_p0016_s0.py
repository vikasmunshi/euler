#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0016/p0016.py :: solve_power_digit_sum_p0016_s0.

Project Euler Problem 16: Power Digit Sum.

Problem Statement:
    2^15 = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.

    What is the sum of the digits of the number 2^1000?

Solution Approach:
    Use fast exponentiation to compute 2^1000 efficiently as a large integer.
    Convert the number to a string and sum its digits.
    The problem involves basic big integer arithmetic and string manipulation.
    Time complexity is dominated by exponentiation, effectively O(log n).

Answer: 1366
URL: https://projecteuler.net/problem=16"""
from __future__ import annotations


def solve(*, base: int, power: int) -> int:
    return sum((int(i) for i in str(base ** power)))


if __name__ == '__main__':
    import sys

    print(solve(base=int(sys.argv[1]), power=int(sys.argv[2])))
