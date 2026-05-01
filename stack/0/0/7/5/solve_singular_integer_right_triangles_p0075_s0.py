#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0075/p0075.py
  func: solve_singular_integer_right_triangles_p0075_s0
"""

from __future__ import annotations

from math import gcd
from sys import argv
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


def main() -> int:
    print(solve(max_perimeter=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
