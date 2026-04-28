#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Migrated from
    euler_solver/solutions/solutions_0001_0100/solution_0075/p0075.py

Project Euler Problem 75: Singular Integer Right Triangles.

Problem Statement:
    It turns out that 12 cm is the smallest length of wire that can be bent to
    form an integer sided right angle triangle in exactly one way, but there are
    many more examples.

    12 cm: (3,4,5)
    24 cm: (6,8,10)
    30 cm: (5,12,13)
    36 cm: (9,12,15)
    40 cm: (8,15,17)
    48 cm: (12,16,20)

    In contrast, some lengths of wire, like 20 cm, cannot be bent to form an
    integer sided right angle triangle, and other lengths allow more than one
    solution to be found; for example, using 120 cm it is possible to form
    exactly three different integer sided right angle triangles.

    120 cm: (30,40,50), (20,48,52), (24,45,51)

    Given that L is the length of the wire, for how many values of L ≤ 1 500 000
    can exactly one integer sided right angle triangle be formed?

Solution Approach:
    Use number theory and Euclid's formula to generate all primitive Pythagorean
    triples. Scale them to find all integer right triangles up to max length L.
    Count wire lengths having exactly one associated triangle using efficient
    aggregation. Time complexity roughly O(L log log L) using a sieve-like approach.

Answer: 161667
URL: https://projecteuler.net/problem=75"""
from __future__ import annotations

from math import gcd
from typing import Dict, Generator


def gen_pythagorean_triangle_perimeters(*, max_perimeter: int) -> Generator[int, None, None]:
    for m in range(2, int((max_perimeter / 2) ** 0.5)):
        for n in range(m % 2 + 1, m, 2):
            if gcd(m, n) != 1:
                continue
            p, k = (2 * m * (m + n), 1)
            while (perimeter := (k * p)) <= max_perimeter:
                yield perimeter
                k += 1


def solve(*, max_perimeter: int) -> int:
    perimeter_count: Dict[int, int] = {}
    for perimeter in gen_pythagorean_triangle_perimeters(max_perimeter=max_perimeter):
        perimeter_count[perimeter] = perimeter_count.get(perimeter, 0) + 1
    return sum((count == 1 for count in perimeter_count.values()))


if __name__ == '__main__':
    import sys

    print(solve(max_perimeter=int(sys.argv[1])))
