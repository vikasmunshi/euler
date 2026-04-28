#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0100/p0100.py :: solve_arranged_probability_p0100_s0.

Project Euler Problem 100: Arranged Probability.

Problem Statement:
    If a box contains twenty-one coloured discs, composed of fifteen blue discs and six
    red discs, and two discs were taken at random, it can be seen that the probability
    of taking two blue discs, P(BB) = (15/21) * (14/20) = 1/2.

    The next such arrangement, for which there is exactly 50% chance of taking two blue
    discs at random, is a box containing eighty-five blue discs and thirty-five red discs.

    By finding the first arrangement to contain over 10^12 = 1,000,000,000,000 discs in
    total, determine the number of blue discs that the box would contain.

Solution Approach:
    Model the problem as a Pell's equation derived from the probability condition.
    Use number theory to find the integer solutions efficiently, exploiting recurrence
    relations for successive solutions. The approach runs in O(log n) time relative to
    the number size, thanks to the rapid growth of solution terms.

Answer: 756872327473
URL: https://projecteuler.net/problem=100"""
from __future__ import annotations


def solve(*, total_discs: int) -> int:
    x, y = (1, 1)
    while True:
        x, y = (3 * x + 4 * y, 2 * x + 3 * y)
        n = (x + 1) // 2
        b = (y + 1) // 2
        if n >= total_discs:
            return b


if __name__ == '__main__':
    import sys

    print(solve(total_discs=int(sys.argv[1])))
