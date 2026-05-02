#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
Migrated from:
  file: euler_solver/solutions/solutions_0001_0100/solution_0039/p0039.py
  func: solve_integer_right_triangles_p0039_s0
"""

from __future__ import annotations

from collections import Counter
from math import gcd
from sys import argv


def solve(*, max_perimeter: int) -> int:
    triangle_perimeters = []
    for n in range(1, (int(8 * max_perimeter**0.5) - 6) // 8, 1):
        for m in (m for m in range(n + 1, (int((4 + 8 * max_perimeter) ** 0.5) - 2 * n) // 4, 2) if gcd(m, n) == 1):
            triangle_perimeters.append((perimeter := (2 * m * (m + n))))
            for k in range(2, max_perimeter // perimeter):
                triangle_perimeters.append(k * perimeter)
    return Counter(triangle_perimeters).most_common()[0][0]


def main() -> int:
    print(solve(max_perimeter=int(argv[1])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
