#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0009/p0009.py :: solve_special_pythagorean_triplet_p0009_s0.

Project Euler Problem 9: Special Pythagorean Triplet.

Problem Statement:
    A Pythagorean triplet is a set of three natural numbers, a < b < c, for which,
    a^2 + b^2 = c^2.

    For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.

    There exists exactly one Pythagorean triplet for which a + b + c = 1000.
    Find the product abc.

Solution Approach:
    Use number theory and algebraic manipulation to reduce the search space.
    Iterate efficiently over pairs (a, b) to find c = 1000 - a - b and check the
    Pythagorean condition. Time complexity O(n^2) is feasible for n=1000.

Answer: 31875000
URL: https://projecteuler.net/problem=9"""
from __future__ import annotations


def solve(*, sum_sides: int) -> int:
    try:
        return next((a * b * c for a in range(1, sum_sides // 4 + 1) for b in range(a, sum_sides // 2) for c in
                     (sum_sides - a - b,) if a ** 2 + b ** 2 == c ** 2))
    except StopIteration:
        raise ValueError(f'No Pythagorean triplet exists with sum {sum_sides}')


if __name__ == '__main__':
    import sys

    print(solve(sum_sides=int(sys.argv[1])))
