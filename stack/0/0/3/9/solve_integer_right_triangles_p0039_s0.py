#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0039/p0039.py :: solve_integer_right_triangles_p0039_s0.

Project Euler Problem 39: Integer Right Triangles.

Problem Statement:
    If p is the perimeter of a right angle triangle with integral length sides,
    {a, b, c}, there are exactly three solutions for p = 120.

    {20,48,52}, {24,45,51}, {30,40,50}

    For which value of p ≤ 1000, is the number of solutions maximised?

Solution Approach:
    Enumerate all integer triples (a, b, c) with a+b+c = p and a^2 + b^2 = c^2.
    Use number theory properties to reduce search space. Efficiently check all p ≤ 1000.
    Use a counting array to record number of solutions for each perimeter.
    Time complexity roughly O(p^2).

Answer: 840
URL: https://projecteuler.net/problem=39"""
from __future__ import annotations

from collections import Counter
from math import gcd


def solve(*, max_perimeter: int) -> int:
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter ** 0.5) - 6) // 8, 1):
        for m in (m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if gcd(m, n) == 1):
            triangle_perimeters.append((perimeter := (2 * m * (m + n))))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return Counter(triangle_perimeters).most_common()[0][0]


if __name__ == '__main__':
    import sys

    print(solve(max_perimeter=int(sys.argv[1])))
