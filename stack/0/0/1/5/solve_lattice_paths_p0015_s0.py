#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0015/p0015.py :: solve_lattice_paths_p0015_s0.

Project Euler Problem 15: Lattice Paths.

Problem Statement:
    Starting in the top left corner of a 2 x 2 grid, and only being able to move
    to the right and down, there are exactly 6 routes to the bottom right corner.

    How many such routes are there through a 20 x 20 grid?

Solution Approach:
    Use combinatorics: the number of lattice paths in an n x n grid equals the
    central binomial coefficient C(2n, n). This can be computed efficiently using
    multiplicative formula or DP with O(n) complexity.

Answer: 137846528820
URL: https://projecteuler.net/problem=15"""
from __future__ import annotations

from math import factorial


def solve(*, lattice_size: int) -> int:
    return factorial(2 * lattice_size) // factorial(lattice_size) ** 2


if __name__ == '__main__':
    import sys

    print(solve(lattice_size=int(sys.argv[1])))
