#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0063/p0063.py :: solve_powerful_digit_counts_p0063_s0.

Project Euler Problem 63: Powerful Digit Counts.

Problem Statement:
    The 5-digit number, 16807=7^5, is also a fifth power. Similarly, the 9-digit
    number, 134217728=8^9, is a ninth power.

    How many n-digit positive integers exist which are also an nth power?

Solution Approach:
    Use number theory and combinatorics. For each base 1 to 9, test powers n
    to find when the length of base^n equals n. Count all such cases.
    Efficiently check digit lengths and powers for small ranges.

Answer: 49
URL: https://projecteuler.net/problem=63"""
from __future__ import annotations

import sys
from math import ceil
from typing import Tuple


def n_digit_nth_powers(n: int) -> Tuple[int, ...]:
    start_range: int = ceil((10 ** (n - 1)) ** (1 / n))
    stop_range: int = ceil((10 ** n - 1) ** (1 / n)) + 1
    return tuple((r for i in range(start_range, stop_range) if len(str((r := (i ** n)))) == n))


def show_solution() -> bool:
    return '--show' in sys.argv


def solve() -> int:
    result: int = 0
    n: int = 1
    while (solutions := n_digit_nth_powers(n)):
        result += len(solutions)
        n += 1
        if show_solution():
            print(f'n={n!r} len(solutions)={len(solutions)!r} solutions={solutions!r} ', file=sys.stderr)
    return result


if __name__ == '__main__':
    print(solve())
