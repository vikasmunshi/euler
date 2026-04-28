#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0092/p0092.py :: solve_square_digit_chains_p0092_s0.

Project Euler Problem 92: Square Digit Chains.

Problem Statement:
    A number chain is created by continuously adding the square of the digits in
    a number to form a new number until it has been seen before.

    For example,
        44 -> 32 -> 13 -> 10 -> 1 -> 1
        85 -> 89 -> 145 -> 42 -> 20 -> 4 -> 16 -> 37 -> 58 -> 89

    Therefore any chain that arrives at 1 or 89 will become stuck in an endless loop.
    What is most amazing is that EVERY starting number will eventually arrive at 1 or 89.

    How many starting numbers below ten million will arrive at 89?

Solution Approach:
    Use caching/memoization for chain ends to avoid recomputation.
    Generate chains by repeatedly summing the squares of digits.
    Count how many numbers below 10 million end at 89.
    Time complexity roughly O(N * d) where d is digit count, optimized by memoization.

Answer: 8581146
URL: https://projecteuler.net/problem=92"""
from __future__ import annotations

import sys
from typing import Dict


def terminates_in_89(n: int) -> bool:
    while n != 1 and n != 89:
        n, t = (0, n)
        while t:
            n, t = (n + (t % 10) ** 2, t // 10)
    return n == 89


def show_solution() -> bool:
    return '--show' in sys.argv


def solve(*, power_of_10: int) -> int:
    a, sq, is89 = ([1], [x ** 2 for x in range(1, 10)], [False])
    results: Dict[int, int] = {}
    for n in range(1, power_of_10 + 1):
        b, a = (a, a + [0] * 81)
        is89 += map(terminates_in_89, range(len(b), len(a)))
        for i, v in enumerate(b):
            for s in sq:
                a[i + s] += v
        results[n] = sum((a[i] for i in range(len(a)) if is89[i]))
    if show_solution():
        print(f'Results for power_of_10={power_of_10}: {results}', file=sys.stderr)
    return results[power_of_10]


if __name__ == '__main__':
    print(solve(power_of_10=int(sys.argv[1])))
