#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0091/p0091.py.

Project Euler Problem 91: Right Triangles with Integer Coordinates.

Problem Statement:
    The points P(x1, y1) and Q(x2, y2) are plotted at integer coordinates and
    are joined to the origin, O(0,0), to form triangle OPQ.

    There are exactly fourteen triangles containing a right angle that can be
    formed when each coordinate lies between 0 and 2 inclusive; that is,
    0 <= x1, y1, x2, y2 <= 2.

    Given that 0 <= x1, y1, x2, y2 <= 50, how many right triangles can be
    formed?

Solution Approach:
    Use coordinate geometry and vector dot product to test for right angles.
    Enumerate all points in the grid and count triples (O, P, Q) with the right
    angle at any vertex using properties of dot products.
    Implementation should be efficient with O(N^2) complexity for N=50.

Answer: 14234
URL: https://projecteuler.net/problem=91"""
from __future__ import annotations

from math import gcd


def solve(*, coordinate_limit: int) -> int:
    triangles_at_p_or_q = sum(
        (min(x * m // y, m * (coordinate_limit - y) // x) for x in range(1, coordinate_limit + 1) for y in
         range(1, coordinate_limit) for m in [gcd(x, y)]))
    triangles_at_p_or_q *= 2
    triangles_at_origin = 3 * coordinate_limit ** 2
    return triangles_at_p_or_q + triangles_at_origin


if __name__ == '__main__':
    import sys

    print(solve(coordinate_limit=int(sys.argv[1])))
