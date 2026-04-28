#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0020/p0020.py :: solve_factorial_digit_sum_p0020_s0.

Project Euler Problem 20: Factorial Digit Sum.

Problem Statement:
    n! means n × (n - 1) × ⋯ × 3 × 2 × 1.

    For example, 10! = 10 × 9 × ⋯ × 3 × 2 × 1 = 3628800,
    and the sum of the digits in the number 10! is 3 + 6 + 2 + 8 + 8 + 0 + 0 = 27.

    Find the sum of the digits in the number 100!.

Solution Approach:
    Use factorial calculation from number theory.
    Convert the factorial result to string and sum its digits.
    Efficient Python arbitrary precision integers allow direct computation.
    Time complexity depends mainly on the multiplication cost for 100!.
    Digit summation is O(digits), feasible for given input.

Answer: 648
URL: https://projecteuler.net/problem=20"""
from __future__ import annotations

from math import factorial


def solve(*, n: int) -> int:
    return sum((int(d) for d in str(factorial(n))))


if __name__ == '__main__':
    import sys

    print(solve(n=int(sys.argv[1])))
